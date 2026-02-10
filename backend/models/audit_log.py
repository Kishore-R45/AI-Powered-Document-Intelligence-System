"""
Audit log model for security and activity tracking.
"""

from datetime import datetime
from bson import ObjectId
from typing import List
from flask import request

from models import mongo


class AuditLog:
    """Audit log model for tracking user activities."""
    
    collection_name = 'audit_logs'
    
    # Action types
    ACTION_LOGIN = 'login'
    ACTION_LOGIN_FAILED = 'login_failed'
    ACTION_LOGOUT = 'logout'
    ACTION_SIGNUP = 'signup'
    ACTION_PASSWORD_CHANGE = 'password_change'
    ACTION_DOCUMENT_UPLOAD = 'document_upload'
    ACTION_DOCUMENT_VIEW = 'document_view'
    ACTION_DOCUMENT_DELETE = 'document_delete'
    ACTION_CHAT_QUERY = 'chat_query'
    ACTION_PROFILE_UPDATE = 'profile_update'
    ACTION_SESSION_LOGOUT_ALL = 'session_logout_all'
    
    @staticmethod
    def log(
        action: str,
        user_id: str = None,
        details: dict = None,
        success: bool = True
    ) -> dict:
        """
        Create an audit log entry.
        
        Args:
            action: Type of action performed
            user_id: User's ID (if authenticated)
            details: Additional details about the action
            success: Whether the action was successful
            
        Returns:
            Created audit log entry
        """
        # Get request context
        ip_address = None
        user_agent = None
        
        try:
            ip_address = request.remote_addr
            user_agent = request.user_agent.string if request.user_agent else None
        except RuntimeError:
            # Outside of request context
            pass
        
        log_entry = {
            'action': action,
            'user_id': ObjectId(user_id) if user_id else None,
            'details': details or {},
            'success': success,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'created_at': datetime.utcnow(),
        }
        
        result = mongo.db.audit_logs.insert_one(log_entry)
        log_entry['_id'] = result.inserted_id
        return log_entry
    
    @staticmethod
    def find_by_user(user_id: str, limit: int = 100) -> List[dict]:
        """Find audit logs for a user."""
        return list(mongo.db.audit_logs.find(
            {'user_id': ObjectId(user_id)}
        ).sort('created_at', -1).limit(limit))
    
    @staticmethod
    def find_by_action(action: str, limit: int = 100) -> List[dict]:
        """Find audit logs by action type."""
        return list(mongo.db.audit_logs.find(
            {'action': action}
        ).sort('created_at', -1).limit(limit))
    
    @staticmethod
    def find_recent_login_attempts(email: str = None, ip_address: str = None, limit: int = 10) -> List[dict]:
        """Find recent login attempts for security analysis."""
        query = {'action': {'$in': [AuditLog.ACTION_LOGIN, AuditLog.ACTION_LOGIN_FAILED]}}
        
        if ip_address:
            query['ip_address'] = ip_address
        
        return list(mongo.db.audit_logs.find(query).sort('created_at', -1).limit(limit))
    
    @staticmethod
    def to_dict(log: dict) -> dict:
        """Convert audit log to dictionary."""
        if not log:
            return None
        return {
            'id': str(log['_id']),
            'action': log.get('action'),
            'user_id': str(log['user_id']) if log.get('user_id') else None,
            'details': log.get('details', {}),
            'success': log.get('success', True),
            'ip_address': log.get('ip_address'),
            'created_at': log.get('created_at').isoformat() if log.get('created_at') else None,
        }
