"""
Expiry reminder job for mobile app.
Checks for expiring documents and sends both email AND push notifications.
"""

from datetime import datetime, timedelta
from models import mongo
from models.document import Document
from models.notification import Notification
from models.user import User
from services.email_service import EmailService
from services.firebase_service import FirebaseService


class ExpiryReminderJob:
    """
    Background job for document expiry reminders.
    Sends email + FCM push notifications.
    """
    
    REMINDER_DAYS = [0, 1, 3, 7, 14, 30]
    
    @classmethod
    def run(cls):
        """Main job entry point."""
        print(f"[{datetime.utcnow()}] Running mobile expiry reminder job...")
        
        reminders_sent = 0
        
        for days in cls.REMINDER_DAYS:
            try:
                reminders_sent += cls._process_expiring_documents(days)
            except Exception as e:
                print(f"Error processing {days}-day reminders: {e}")
                import traceback
                traceback.print_exc()
        
        try:
            expired_notifications = cls.check_expired()
        except Exception as e:
            print(f"Error checking expired documents: {e}")
            expired_notifications = 0
        
        print(f"[{datetime.utcnow()}] Expiry reminder job complete. {reminders_sent} reminders, {expired_notifications} expired notifications.")
        return reminders_sent + expired_notifications
    
    @classmethod
    def _strip_timezone(cls, dt):
        """Strip timezone info for comparison with naive datetimes."""
        if dt is None:
            return None
        if dt.tzinfo is not None:
            return dt.replace(tzinfo=None)
        return dt
    
    @classmethod
    def _process_expiring_documents(cls, days: int) -> int:
        """Process documents expiring in specified days."""
        now = datetime.utcnow()
        
        target_date_start = (now + timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
        target_date_end = target_date_start + timedelta(days=1)
        
        documents = list(mongo.db.documents.find({
            'has_expiry': True,
            'expiry_date': {
                '$gte': target_date_start,
                '$lt': target_date_end
            }
        }))
        
        reminders_sent = 0
        
        for doc in documents:
            try:
                user_id = str(doc['user_id'])
                user = User.find_by_id(user_id)
                if not user or not user.get('is_active'):
                    continue
                
                # Check if already sent today
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                existing = mongo.db.notifications.find_one({
                    'user_id': doc['user_id'],
                    'type': Notification.TYPE_EXPIRY_REMINDER,
                    'metadata.reminder_days': days,
                    'metadata.document_id': str(doc['_id']),
                    'created_at': {'$gte': today_start}
                })
                
                if existing:
                    continue
                
                expiry_date = cls._strip_timezone(doc.get('expiry_date'))
                if not expiry_date:
                    continue
                
                if days == 0:
                    title = "Document Expires Today!"
                    message = f"'{doc.get('name')}' expires TODAY ({expiry_date.strftime('%B %d, %Y')})!"
                elif days == 1:
                    title = "Document Expires Tomorrow"
                    message = f"'{doc.get('name')}' will expire TOMORROW ({expiry_date.strftime('%B %d, %Y')})."
                else:
                    title = f"Document Expiring in {days} Days"
                    message = f"'{doc.get('name')}' will expire on {expiry_date.strftime('%B %d, %Y')} ({days} days remaining)."
                
                # Create notification with push
                Notification.create(
                    user_id=user_id,
                    notification_type=Notification.TYPE_EXPIRY_REMINDER,
                    title=title,
                    message=message,
                    document_id=str(doc['_id']),
                    metadata={'reminder_days': days, 'document_id': str(doc['_id'])},
                    send_push=True
                )
                
                # Send FCM push explicitly with expiry data
                try:
                    FirebaseService.send_expiry_reminder(
                        user_id=user_id,
                        document_name=doc.get('name', 'Unknown'),
                        days_until_expiry=days
                    )
                except Exception as push_err:
                    print(f"  Push notification failed: {push_err}")
                
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
                
                reminders_sent += 1
                
            except Exception as e:
                print(f"  Error processing document {doc.get('_id')}: {e}")
                continue
        
        return reminders_sent
    
    @classmethod
    def check_expired(cls) -> int:
        """Check for expired documents and notify."""
        now = datetime.utcnow()
        
        documents = list(mongo.db.documents.find({
            'has_expiry': True,
            'expiry_date': {'$lt': now}
        }))
        
        notifications_sent = 0
        
        for doc in documents:
            try:
                existing = mongo.db.notifications.find_one({
                    'user_id': doc['user_id'],
                    'type': Notification.TYPE_EXPIRED,
                    'metadata.document_id': str(doc['_id'])
                })
                
                if existing:
                    continue
                
                expiry_date = cls._strip_timezone(doc.get('expiry_date'))
                expiry_str = expiry_date.strftime('%B %d, %Y') if expiry_date else 'Unknown'
                
                # Create expired notification with push
                Notification.create(
                    user_id=str(doc['user_id']),
                    notification_type=Notification.TYPE_EXPIRED,
                    title="Document Expired",
                    message=f"'{doc.get('name')}' has expired on {expiry_str}. Please renew or update.",
                    document_id=str(doc['_id']),
                    metadata={'document_id': str(doc['_id'])},
                    send_push=True
                )
                
                # Send email
                user = User.find_by_id(str(doc['user_id']))
                if user and user.get('is_active'):
                    EmailService.send_expiry_reminder(
                        to_email=user['email'],
                        document_name=doc.get('name', 'Unknown'),
                        expiry_date=expiry_str,
                        days_until_expiry=0,
                        name=user.get('name')
                    )
                    
                    # Send expired push notification
                    try:
                        FirebaseService.send_expiry_reminder(
                            user_id=str(doc['user_id']),
                            document_name=doc.get('name', 'Unknown'),
                            days_until_expiry=-1
                        )
                    except Exception as push_err:
                        print(f"  Expired push notification failed: {push_err}")
                
                notifications_sent += 1
                
            except Exception as e:
                print(f"  Error processing expired document {doc.get('_id')}: {e}")
                continue
        
        return notifications_sent
