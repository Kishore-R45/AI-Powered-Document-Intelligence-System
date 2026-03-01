"""
User model with biometric and FCM support for mobile app.
"""

from datetime import datetime
from bson import ObjectId
import bcrypt

from models import mongo


class User:
    """User model with mobile-specific features."""
    
    collection_name = 'users'
    
    @staticmethod
    def create(name: str, email: str, password: str, is_active: bool = False) -> dict:
        """Create a new user."""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user = {
            'name': name,
            'email': email.lower().strip(),
            'password': hashed_password,
            'is_active': is_active,
            'biometric_enabled': False,
            'biometric_public_key': None,
            'fcm_tokens': [],  # List of FCM device tokens
            'trusted_devices': [],  # List of trusted device IDs
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        result = mongo.db.users.insert_one(user)
        user['_id'] = result.inserted_id
        return user
    
    @staticmethod
    def find_by_email(email: str) -> dict | None:
        """Find a user by email address."""
        return mongo.db.users.find_one({'email': email.lower().strip()})
    
    @staticmethod
    def find_by_id(user_id: str) -> dict | None:
        """Find a user by ID."""
        try:
            return mongo.db.users.find_one({'_id': ObjectId(user_id)})
        except Exception:
            return None
    
    @staticmethod
    def activate(email: str) -> bool:
        """Activate a user account after OTP verification."""
        result = mongo.db.users.update_one(
            {'email': email.lower().strip()},
            {'$set': {'is_active': True, 'updated_at': datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def verify_password(user: dict, password: str) -> bool:
        """Verify a password against the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), user['password'])
    
    @staticmethod
    def update_password(user_id: str, new_password: str) -> bool:
        """Update a user's password."""
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        result = mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password': hashed_password, 'updated_at': datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def update(user_id: str, fields: dict) -> bool:
        """Update user fields."""
        fields['updated_at'] = datetime.utcnow()
        fields.pop('password', None)
        fields.pop('email', None)
        fields.pop('is_active', None)
        
        result = mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': fields}
        )
        return result.modified_count > 0
    
    @staticmethod
    def enable_biometric(user_id: str, device_id: str) -> bool:
        """Enable biometric authentication for a user."""
        result = mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'biometric_enabled': True,
                    'updated_at': datetime.utcnow()
                },
                '$addToSet': {'trusted_devices': device_id}
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def disable_biometric(user_id: str) -> bool:
        """Disable biometric authentication for a user."""
        result = mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'biometric_enabled': False,
                    'biometric_public_key': None,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def add_fcm_token(user_id: str, fcm_token: str) -> bool:
        """Add an FCM token for push notifications."""
        result = mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$addToSet': {'fcm_tokens': fcm_token},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def remove_fcm_token(user_id: str, fcm_token: str) -> bool:
        """Remove an FCM token."""
        result = mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$pull': {'fcm_tokens': fcm_token},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    @staticmethod
    def get_fcm_tokens(user_id: str) -> list:
        """Get all FCM tokens for a user."""
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)}, {'fcm_tokens': 1})
        return user.get('fcm_tokens', []) if user else []
    
    @staticmethod
    def exists(email: str) -> bool:
        """Check if a user with the given email exists."""
        return mongo.db.users.count_documents({'email': email.lower().strip()}) > 0
    
    @staticmethod
    def to_dict(user: dict) -> dict:
        """Convert user document to safe dictionary for API response."""
        if not user:
            return None
        return {
            'id': str(user['_id']),
            'name': user.get('name'),
            'email': user.get('email'),
            'isActive': user.get('is_active', False),
            'biometricEnabled': user.get('biometric_enabled', False),
            'createdAt': user.get('created_at').isoformat() if user.get('created_at') else None,
        }
