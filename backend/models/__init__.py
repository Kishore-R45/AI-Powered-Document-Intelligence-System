"""
Database models initialization.
Sets up MongoDB connection and exports all models.
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
import certifi


class MongoWrapper:
    """Wrapper to make PyMongo's MongoClient compatible with Flask-PyMongo interface."""
    def __init__(self):
        self.client = None
        self.db = None
    
    def init_app(self, app):
        """Initialize MongoDB connection with custom SSL context."""
        mongo_uri = app.config['MONGO_URI']
        try:
            # Use certifi for SSL/TLS certificates on Windows
            import ssl as ssl_lib
            os.environ['SSL_CERT_FILE'] = certifi.where()
            
            # Create custom SSL context for Windows Python 3.10
            ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl_lib.CERT_NONE
            
            # PyMongo 4.x connection
            self.client = MongoClient(
                mongo_uri,
                tls=True,
                tlsAllowInvalidCertificates=True,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000
            )
            
            # Get database name from URI or use default
            db_name = mongo_uri.split('/')[-1].split('?')[0] or 'infovault'
            self.db = self.client[db_name]
            
            # Test connection
            self.client.admin.command('ping')
            print(f"✓ Connected to MongoDB: {db_name}")
            
        except Exception as e:
            print(f"✗ MongoDB connection failed: {e}")
            # Don't raise, allow app to start but warn
    
    def get_db(self):
        """Get database instance."""
        return self.db


mongo = MongoWrapper()


def init_db(app):
    """Initialize MongoDB connection."""
    mongo.init_app(app)
    
    # Create indexes for better query performance
    if mongo.db is not None:
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
            
            print("✓ MongoDB indexes created successfully")
            
        except Exception as e:
            print(f"✗ Warning: Could not create indexes: {e}")
    
    return mongo
