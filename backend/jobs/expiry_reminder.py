"""
Expiry reminder job.
Checks for expiring documents and sends notifications/emails.
Handles timezone-aware and naive datetime comparisons.
"""

from datetime import datetime, timedelta
from typing import List

from models import mongo
from models.document import Document
from models.notification import Notification
from models.user import User
from services.email_service import EmailService


class ExpiryReminderJob:
    """
    Background job for document expiry reminders.
    Should be run daily via scheduler (APScheduler, Celery, or cron).
    Can also be triggered manually via /api/dashboard/trigger-expiry-check
    """
    
    REMINDER_DAYS = [0, 1, 3, 7, 14, 30]  # Send reminders at these days before expiry
    
    @classmethod
    def run(cls):
        """
        Main job entry point.
        Checks all documents and sends appropriate reminders.
        """
        print(f"[{datetime.utcnow()}] Running expiry reminder job...")
        
        reminders_sent = 0
        
        for days in cls.REMINDER_DAYS:
            try:
                reminders_sent += cls._process_expiring_documents(days)
            except Exception as e:
                print(f"Error processing {days}-day reminders: {e}")
                import traceback
                traceback.print_exc()
        
        # Also check for already expired documents
        try:
            expired_notifications = cls.check_expired()
        except Exception as e:
            print(f"Error checking expired documents: {e}")
            expired_notifications = 0
        
        print(f"[{datetime.utcnow()}] Expiry reminder job complete. Sent {reminders_sent} reminders, {expired_notifications} expired notifications.")
        return reminders_sent + expired_notifications
    
    @classmethod
    def _strip_timezone(cls, dt):
        """Strip timezone info from datetime for comparison with naive datetimes."""
        if dt is None:
            return None
        if dt.tzinfo is not None:
            return dt.replace(tzinfo=None)
        return dt
    
    @classmethod
    def _process_expiring_documents(cls, days: int) -> int:
        """
        Process documents expiring in specified days.
        
        Args:
            days: Number of days until expiry
            
        Returns:
            Number of reminders sent
        """
        now = datetime.utcnow()
        
        # Calculate the target date range
        # For days=1, we want documents expiring between tomorrow 00:00 and tomorrow 23:59
        target_date_start = (now + timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
        target_date_end = target_date_start + timedelta(days=1)
        
        print(f"  Checking documents expiring in {days} day(s): {target_date_start} to {target_date_end}")
        
        # Find documents expiring in the target range
        documents = list(mongo.db.documents.find({
            'has_expiry': True,
            'expiry_date': {
                '$gte': target_date_start,
                '$lt': target_date_end
            }
        }))
        
        print(f"  Found {len(documents)} documents expiring in {days} day(s)")
        
        reminders_sent = 0
        
        for doc in documents:
            try:
                user_id = str(doc['user_id'])
                user = User.find_by_id(user_id)
                if not user or not user.get('is_active'):
                    print(f"  Skipping document {doc['_id']}: user inactive or not found")
                    continue
                
                # Check if we already sent a reminder for this document/day combination today
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                existing_notification = mongo.db.notifications.find_one({
                    'user_id': doc['user_id'],
                    'type': Notification.TYPE_EXPIRY_REMINDER,
                    'metadata.reminder_days': days,
                    'metadata.document_id': str(doc['_id']),
                    'created_at': {'$gte': today_start}
                })
                
                if existing_notification:
                    print(f"  Skipping document {doc['_id']}: reminder already sent today for {days}-day window")
                    continue
                
                # Get expiry date, strip timezone if needed
                expiry_date = cls._strip_timezone(doc.get('expiry_date'))
                if not expiry_date:
                    continue
                
                # Create notification with appropriate title
                if days == 0:
                    title = "Document Expires Today!"
                    message = f"'{doc.get('name')}' expires TODAY ({expiry_date.strftime('%B %d, %Y')})! Please take immediate action."
                elif days == 1:
                    title = "Document Expires Tomorrow"
                    message = f"'{doc.get('name')}' will expire TOMORROW ({expiry_date.strftime('%B %d, %Y')}). Please renew it soon."
                else:
                    title = f"Document Expiring in {days} Days"
                    message = f"'{doc.get('name')}' will expire on {expiry_date.strftime('%B %d, %Y')} ({days} days remaining)."
                
                Notification.create(
                    user_id=user_id,
                    notification_type=Notification.TYPE_EXPIRY_REMINDER,
                    title=title,
                    message=message,
                    document_id=str(doc['_id']),
                    metadata={'reminder_days': days, 'document_id': str(doc['_id'])}
                )
                
                # Send email
                expiry_formatted = expiry_date.strftime('%B %d, %Y')
                email_sent = EmailService.send_expiry_reminder(
                    to_email=user['email'],
                    document_name=doc.get('name', 'Unknown'),
                    expiry_date=expiry_formatted,
                    days_until_expiry=days,
                    name=user.get('name')
                )
                
                if email_sent:
                    print(f"  ✓ Sent {days}-day reminder for '{doc.get('name')}' to {user['email']}")
                else:
                    print(f"  ✗ Failed to send email for '{doc.get('name')}' to {user['email']}")
                
                reminders_sent += 1
                
            except Exception as e:
                print(f"  Error processing document {doc.get('_id')}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        return reminders_sent
    
    @classmethod
    def check_expired(cls) -> int:
        """
        Check for documents that have expired.
        Sends notifications for any expired documents that haven't been notified yet.
        
        Returns:
            Number of expiry notifications sent
        """
        now = datetime.utcnow()
        
        # Find all expired documents (expiry_date < now)
        documents = list(mongo.db.documents.find({
            'has_expiry': True,
            'expiry_date': {
                '$lt': now
            }
        }))
        
        print(f"  Found {len(documents)} expired documents")
        
        notifications_sent = 0
        
        for doc in documents:
            try:
                # Check if we already sent an expired notification for this document
                existing = mongo.db.notifications.find_one({
                    'user_id': doc['user_id'],
                    'type': Notification.TYPE_EXPIRED,
                    'metadata.document_id': str(doc['_id'])
                })
                
                if existing:
                    continue
                
                expiry_date = cls._strip_timezone(doc.get('expiry_date'))
                expiry_str = expiry_date.strftime('%B %d, %Y') if expiry_date else 'Unknown'
                
                # Create expired notification
                Notification.create(
                    user_id=str(doc['user_id']),
                    notification_type=Notification.TYPE_EXPIRED,
                    title="Document Expired",
                    message=f"'{doc.get('name')}' has expired on {expiry_str}. Please renew or update this document.",
                    document_id=str(doc['_id']),
                    metadata={'document_id': str(doc['_id'])}
                )
                
                # Send email notification for expired document
                user = User.find_by_id(str(doc['user_id']))
                if user and user.get('is_active'):
                    EmailService.send_expiry_reminder(
                        to_email=user['email'],
                        document_name=doc.get('name', 'Unknown'),
                        expiry_date=expiry_str,
                        days_until_expiry=0,
                        name=user.get('name')
                    )
                
                notifications_sent += 1
                
            except Exception as e:
                print(f"  Error processing expired document {doc.get('_id')}: {e}")
                continue
        
        return notifications_sent
