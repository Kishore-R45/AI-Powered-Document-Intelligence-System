"""
Notification model and related operations.
"""

from datetime import datetime
from bson import ObjectId
from typing import List

from models import mongo


class Notification:
    """Notification model for user alerts and reminders."""
    
    collection_name = 'notifications'
    
    # Notification types
    TYPE_UPLOAD = 'upload'
    TYPE_DELETE = 'delete'
    TYPE_EXPIRY_REMINDER = 'expiry_reminder'
    TYPE_EXPIRED = 'expired'
    TYPE_SECURITY = 'security'
    TYPE_SYSTEM = 'system'
    
    @staticmethod
    def create(
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        document_id: str = None,
        metadata: dict = None
    ) -> dict:
        """
        Create a new notification.
        
        Args:
            user_id: User's ID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            document_id: Related document ID if applicable
            metadata: Additional metadata
            
        Returns:
            Created notification document
        """
        notification = {
            'user_id': ObjectId(user_id),
            'type': notification_type,
            'title': title,
            'message': message,
            'document_id': ObjectId(document_id) if document_id else None,
            'metadata': metadata or {},
            'read': False,
            'created_at': datetime.utcnow(),
        }
        
        result = mongo.db.notifications.insert_one(notification)
        notification['_id'] = result.inserted_id
        return notification
    
    @staticmethod
    def find_by_user(user_id: str, limit: int = 50, unread_only: bool = False) -> List[dict]:
        """Find notifications for a user."""
        query = {'user_id': ObjectId(user_id)}
        if unread_only:
            query['read'] = False
        
        return list(mongo.db.notifications.find(query)
                    .sort('created_at', -1)
                    .limit(limit))
    
    @staticmethod
    def count_unread(user_id: str) -> int:
        """Count unread notifications for a user."""
        return mongo.db.notifications.count_documents({
            'user_id': ObjectId(user_id),
            'read': False
        })
    
    @staticmethod
    def mark_as_read(notification_id: str, user_id: str) -> bool:
        """Mark a notification as read."""
        result = mongo.db.notifications.update_one(
            {'_id': ObjectId(notification_id), 'user_id': ObjectId(user_id)},
            {'$set': {'read': True}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def mark_all_as_read(user_id: str) -> int:
        """Mark all notifications as read for a user."""
        result = mongo.db.notifications.update_many(
            {'user_id': ObjectId(user_id), 'read': False},
            {'$set': {'read': True}}
        )
        return result.modified_count
    
    @staticmethod
    def delete(notification_id: str, user_id: str) -> bool:
        """Delete a notification."""
        result = mongo.db.notifications.delete_one({
            '_id': ObjectId(notification_id),
            'user_id': ObjectId(user_id)
        })
        return result.deleted_count > 0
    
    @staticmethod
    def delete_old(days: int = 30) -> int:
        """Delete notifications older than specified days."""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = mongo.db.notifications.delete_many({'created_at': {'$lt': cutoff}})
        return result.deleted_count
    
    @staticmethod
    def to_dict(notification: dict) -> dict:
        """Convert notification to dictionary."""
        if not notification:
            return None
        created_at = notification.get('created_at')
        created_at_iso = created_at.isoformat() if created_at else None
        return {
            'id': str(notification['_id']),
            'type': notification.get('type'),
            'title': notification.get('title'),
            'message': notification.get('message'),
            'document_id': str(notification['document_id']) if notification.get('document_id') else None,
            'metadata': notification.get('metadata', {}),
            'read': notification.get('read', False),
            'created_at': created_at_iso,
            'timestamp': created_at_iso,
        }
