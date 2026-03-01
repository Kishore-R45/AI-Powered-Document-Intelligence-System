"""
Session model with persistent session support for mobile app.
Supports trusted devices, biometric sessions, and offline mode.
"""

from datetime import datetime, timedelta
from bson import ObjectId
from typing import List

from models import mongo
from config import Config


class Session:
    """Session model with mobile-specific persistent session support."""
    
    collection_name = 'sessions'
    
    SESSION_TYPE_STANDARD = 'standard'
    SESSION_TYPE_BIOMETRIC = 'biometric'
    SESSION_TYPE_REFRESH = 'refresh'
    
    @staticmethod
    def create(
        user_id: str,
        token_jti: str,
        expires_at: datetime = None,
        ip_address: str = None,
        user_agent: str = None,
        device_id: str = None,
        session_type: str = 'standard'
    ) -> dict:
        """Create a new session entry with device tracking."""
        if expires_at is None:
            if session_type == 'biometric':
                expires_at = datetime.utcnow() + Config.JWT_BIOMETRIC_TOKEN_EXPIRES
            elif session_type == 'refresh':
                expires_at = datetime.utcnow() + Config.JWT_REFRESH_TOKEN_EXPIRES
            else:
                expires_at = datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
        
        session = {
            'user_id': ObjectId(user_id),
            'token_jti': token_jti,
            'session_type': session_type,
            'device_id': device_id,
            'created_at': datetime.utcnow(),
            'last_active': datetime.utcnow(),
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
            return True  # Backward compatibility
        return not session.get('revoked', False)
    
    @staticmethod
    def update_last_active(token_jti: str) -> bool:
        """Update last active timestamp for a session."""
        result = mongo.db.sessions.update_one(
            {'token_jti': token_jti, 'revoked': False},
            {'$set': {'last_active': datetime.utcnow()}}
        )
        return result.modified_count > 0
    
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
        """Check if this login is from a new/different device."""
        previous_sessions = list(mongo.db.sessions.find({
            'user_id': ObjectId(user_id),
        }).sort('created_at', -1).limit(20))
        
        if not previous_sessions:
            return False
        
        for session in previous_sessions:
            prev_ip = session.get('ip_address')
            prev_ua = session.get('user_agent')
            if prev_ip == ip_address or prev_ua == user_agent:
                return False
        
        return True
    
    @staticmethod
    def find_by_device(user_id: str, device_id: str) -> dict | None:
        """Find an active session for a specific device."""
        return mongo.db.sessions.find_one({
            'user_id': ObjectId(user_id),
            'device_id': device_id,
            'revoked': False,
            'expires_at': {'$gt': datetime.utcnow()}
        })
    
    @staticmethod
    def to_dict(session: dict) -> dict:
        """Convert session to dictionary."""
        if not session:
            return None
        return {
            'id': str(session['_id']),
            'sessionType': session.get('session_type', 'standard'),
            'deviceId': session.get('device_id'),
            'createdAt': session.get('created_at').isoformat() if session.get('created_at') else None,
            'lastActive': session.get('last_active').isoformat() if session.get('last_active') else None,
            'expiresAt': session.get('expires_at').isoformat() if session.get('expires_at') else None,
            'ipAddress': session.get('ip_address'),
            'userAgent': session.get('user_agent'),
        }
