"""
Session model for managing JWT tokens and logout-all functionality.
"""

from datetime import datetime, timedelta
from bson import ObjectId
from typing import List

from models import mongo
from config import Config


class Session:
    """Session model for token management."""
    
    collection_name = 'sessions'
    
    @staticmethod
    def create(user_id: str, token_jti: str, expires_at: datetime = None, ip_address: str = None, user_agent: str = None) -> dict:
        """
        Create a new session entry.
        
        Args:
            user_id: User's ID
            token_jti: JWT token ID (jti claim)
            expires_at: Token expiry time
            ip_address: Client IP address
            user_agent: Client user agent string
            
        Returns:
            Created session entry
        """
        if expires_at is None:
            expires_at = datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
        
        session = {
            'user_id': ObjectId(user_id),
            'token_jti': token_jti,
            'created_at': datetime.utcnow(),
            'expires_at': expires_at,
            'revoked': False,
            'ip_address': ip_address,
            'user_agent': user_agent,
        }
        
        result = mongo.db.sessions.insert_one(session)
        session['_id'] = result.inserted_id
        return session
    
    @staticmethod
    def find_by_jti(token_jti: str) -> dict | None:
        """Find a session by JWT ID."""
        return mongo.db.sessions.find_one({'token_jti': token_jti})
    
    @staticmethod
    def is_valid(token_jti: str) -> bool:
        """Check if a session is valid (exists and not revoked)."""
        session = mongo.db.sessions.find_one({'token_jti': token_jti})
        if not session:
            return True  # Session not tracked, assume valid (for backward compatibility)
        return not session.get('revoked', False)
    
    @staticmethod
    def revoke(token_jti: str) -> bool:
        """Revoke a specific session."""
        result = mongo.db.sessions.update_one(
            {'token_jti': token_jti},
            {'$set': {'revoked': True}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def revoke_all_for_user(user_id: str) -> int:
        """Revoke all sessions for a user (logout-all)."""
        result = mongo.db.sessions.update_many(
            {'user_id': ObjectId(user_id), 'revoked': False},
            {'$set': {'revoked': True}}
        )
        return result.modified_count
    
    @staticmethod
    def cleanup_expired() -> int:
        """Clean up expired sessions."""
        result = mongo.db.sessions.delete_many({
            'expires_at': {'$lt': datetime.utcnow()}
        })
        return result.deleted_count
    
    @staticmethod
    def get_active_sessions(user_id: str) -> List[dict]:
        """Get all active sessions for a user."""
        return list(mongo.db.sessions.find({
            'user_id': ObjectId(user_id),
            'revoked': False,
            'expires_at': {'$gt': datetime.utcnow()}
        }).sort('created_at', -1))
    
    @staticmethod
    def is_new_device(user_id: str, ip_address: str, user_agent: str) -> bool:
        """
        Check if this login is from a new/different device.
        Compares IP + user agent with previous sessions.
        Returns False if no previous sessions exist (new account).
        
        Args:
            user_id: User's ID
            ip_address: Client IP
            user_agent: Client user agent string
            
        Returns:
            True if this is a new device, False otherwise
        """
        # Check if user has any previous sessions at all
        previous_sessions = list(mongo.db.sessions.find({
            'user_id': ObjectId(user_id),
        }).sort('created_at', -1).limit(20))
        
        if not previous_sessions:
            # No previous sessions - first login after registration, not a new device alert
            return False
        
        # Check if any previous session matches this IP or user agent
        for session in previous_sessions:
            prev_ip = session.get('ip_address')
            prev_ua = session.get('user_agent')
            
            # Match on IP address OR user agent (same device/browser can change networks)
            if prev_ip == ip_address or prev_ua == user_agent:
                return False
        
        return True
