"""
Database models initialization.
Sets up MongoDB connection and exports all models.
"""

from flask_pymongo import PyMongo

mongo = PyMongo()


def init_db(app):
    """Initialize MongoDB connection."""
    mongo.init_app(app)
    
    # Create indexes for better query performance
    with app.app_context():
        try:
            # User indexes
            mongo.db.users.create_index('email', unique=True)
            
            # Document indexes
            mongo.db.documents.create_index('user_id')
            mongo.db.documents.create_index([('user_id', 1), ('created_at', -1)])
            mongo.db.documents.create_index('expiry_date')
            
            # OTP indexes
            mongo.db.otps.create_index('email')
            mongo.db.otps.create_index('expires_at', expireAfterSeconds=0)
            
            # Notification indexes
            mongo.db.notifications.create_index([('user_id', 1), ('created_at', -1)])
            mongo.db.notifications.create_index([('user_id', 1), ('read', 1)])
            
            # Audit log indexes
            mongo.db.audit_logs.create_index([('user_id', 1), ('created_at', -1)])
            mongo.db.audit_logs.create_index('action')
            
            # Chat history indexes
            mongo.db.chat_history.create_index([('user_id', 1), ('created_at', -1)])
            
            # Session indexes (for logout-all functionality)
            mongo.db.sessions.create_index('user_id')
            mongo.db.sessions.create_index('token_jti', unique=True)
            mongo.db.sessions.create_index('expires_at', expireAfterSeconds=0)
            
        except Exception as e:
            print(f"Warning: Could not create indexes: {e}")
    
    return mongo
