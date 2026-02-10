"""
Expiry reminder job.
Checks for expiring documents and sends notifications/emails.
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
    """
    
    REMINDER_DAYS = [1, 7]  # Send reminders at 1 day and 7 days before expiry
    
    @classmethod
    def run(cls):
        """
        Main job entry point.
        Checks all documents and sends appropriate reminders.
        """
        print(f"[{datetime.utcnow()}] Running expiry reminder job...")
        
        reminders_sent = 0
        
        for days in cls.REMINDER_DAYS:
            reminders_sent += cls._process_expiring_documents(days)
        
        print(f"[{datetime.utcnow()}] Expiry reminder job complete. Sent {reminders_sent} reminders.")
        return reminders_sent
    
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
        target_date_start = now + timedelta(days=days)
        target_date_end = target_date_start + timedelta(days=1)
        
        # Find documents expiring on the target date
        documents = list(mongo.db.documents.find({
            'has_expiry': True,
            'expiry_date': {
                '$gte': target_date_start.replace(hour=0, minute=0, second=0),
                '$lt': target_date_end.replace(hour=0, minute=0, second=0)
            }
        }))
        
        reminders_sent = 0
        
        for doc in documents:
            try:
                user = User.find_by_id(str(doc['user_id']))
                if not user or not user.get('is_active'):
                    continue
                
                # Check if we already sent a reminder for this document/day combination
                existing_notification = mongo.db.notifications.find_one({
                    'document_id': doc['_id'],
                    'type': Notification.TYPE_EXPIRY_REMINDER,
                    'metadata.reminder_days': days,
                    'created_at': {'$gte': now.replace(hour=0, minute=0, second=0)}
                })
                
                if existing_notification:
                    continue  # Already sent today
                
                # Create notification
                Notification.create(
                    user_id=str(doc['user_id']),
                    notification_type=Notification.TYPE_EXPIRY_REMINDER,
                    title=f"Document Expiring in {days} Day{'s' if days > 1 else ''}",
                    message=f"'{doc.get('name')}' will expire on {doc['expiry_date'].strftime('%B %d, %Y')}.",
                    document_id=str(doc['_id']),
                    metadata={'reminder_days': days}
                )
                
                # Send email
                expiry_formatted = doc['expiry_date'].strftime('%B %d, %Y')
                EmailService.send_expiry_reminder(
                    to_email=user['email'],
                    document_name=doc.get('name', 'Unknown'),
                    expiry_date=expiry_formatted,
                    days_until_expiry=days,
                    name=user.get('name')
                )
                
                reminders_sent += 1
                
            except Exception as e:
                print(f"Error processing document {doc.get('_id')}: {e}")
                continue
        
        return reminders_sent
    
    @classmethod
    def check_expired(cls) -> int:
        """
        Check for documents that have just expired (today).
        
        Returns:
            Number of expiry notifications sent
        """
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        
        # Find documents that expired in the last 24 hours
        documents = list(mongo.db.documents.find({
            'has_expiry': True,
            'expiry_date': {
                '$gte': yesterday,
                '$lt': now
            }
        }))
        
        notifications_sent = 0
        
        for doc in documents:
            try:
                # Check if we already sent an expired notification
                existing = mongo.db.notifications.find_one({
                    'document_id': doc['_id'],
                    'type': Notification.TYPE_EXPIRED
                })
                
                if existing:
                    continue
                
                # Create expired notification
                Notification.create(
                    user_id=str(doc['user_id']),
                    notification_type=Notification.TYPE_EXPIRED,
                    title="Document Expired",
                    message=f"'{doc.get('name')}' has expired.",
                    document_id=str(doc['_id'])
                )
                
                notifications_sent += 1
                
            except Exception as e:
                print(f"Error processing expired document {doc.get('_id')}: {e}")
                continue
        
        return notifications_sent
