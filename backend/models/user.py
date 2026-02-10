"""
User model and related operations.
"""

from datetime import datetime
from bson import ObjectId
import bcrypt

from models import mongo


class User:
    """User model for authentication and profile management."""
    
    collection_name = 'users'
    
    @staticmethod
    def create(name: str, email: str, password: str, is_active: bool = False) -> dict:
        """
        Create a new user.
        
        Args:
            name: User's full name
            email: User's email address
            password: Plain text password (will be hashed)
            is_active: Whether the account is activated
            
        Returns:
            Created user document
        """
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user = {
            'name': name,
            'email': email.lower().strip(),
            'password': hashed_password,
            'is_active': is_active,
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
        # Don't allow updating sensitive fields directly
        fields.pop('password', None)
        fields.pop('email', None)
        fields.pop('is_active', None)
        
        result = mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': fields}
        )
        return result.modified_count > 0
    
    @staticmethod
    def to_dict(user: dict) -> dict:
        """Convert user document to safe dictionary (no password)."""
        if not user:
            return None
        return {
            'id': str(user['_id']),
            'name': user.get('name'),
            'email': user.get('email'),
            'is_active': user.get('is_active', False),
            'created_at': user.get('created_at').isoformat() if user.get('created_at') else None,
        }
    
    @staticmethod
    def exists(email: str) -> bool:
        """Check if a user with the given email exists."""
        return mongo.db.users.count_documents({'email': email.lower().strip()}) > 0
