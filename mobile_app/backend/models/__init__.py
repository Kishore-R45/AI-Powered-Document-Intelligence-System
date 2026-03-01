"""
Database models initialization for mobile backend.
Sets up MongoDB connection and exports all models.
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
import certifi


class MongoWrapper:
    """Wrapper for MongoDB connection management."""
    def __init__(self):
        self.client = None
        self.db = None
    
    def init_app(self, app):
        """Initialize MongoDB connection."""
        mongo_uri = app.config['MONGO_URI']
        try:
            import ssl as ssl_lib
            os.environ['SSL_CERT_FILE'] = certifi.where()
            
            self.client = MongoClient(
                mongo_uri,
                tls=True,
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=15000,
                connectTimeoutMS=15000,
                socketTimeoutMS=15000,
                retryWrites=True,
                retryReads=True,
                maxPoolSize=50,
                minPoolSize=10,
            )
            
            db_name = mongo_uri.split('/')[-1].split('?')[0] or 'infovault_mobile'
            self.db = self.client[db_name]
            
            retry_count = 3
            for attempt in range(retry_count):
                try:
                    self.client.admin.command('ping')
                    print(f"✓ Connected to MongoDB: {db_name}")
                    break
                except Exception as ping_error:
                    if attempt < retry_count - 1:
                        print(f"  MongoDB connection attempt {attempt + 1} failed, retrying...")
                        import time
                        time.sleep(2)
                    else:
                        raise ping_error
            
        except Exception as e:
            print(f"✗ MongoDB connection failed: {e}")
    
    def get_db(self):
        """Get database instance."""
        return self.db


mongo = MongoWrapper()


def init_db(app):
    """Initialize MongoDB connection and create indexes."""
    mongo.init_app(app)
    
    if mongo.db is not None:
        try:
            # User indexes
            mongo.db.users.create_index('email', unique=True)
            mongo.db.users.create_index('fcm_tokens')
            
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
            
            # Session indexes
            mongo.db.sessions.create_index('user_id')
            mongo.db.sessions.create_index('token_jti', unique=True)
            mongo.db.sessions.create_index('expires_at', expireAfterSeconds=0)
            
            # Trusted device indexes
            mongo.db.trusted_devices.create_index('user_id')
            mongo.db.trusted_devices.create_index('device_id', unique=True)
            mongo.db.trusted_devices.create_index([('user_id', 1), ('device_id', 1)])
            
            # Extracted data indexes
            mongo.db.extracted_data.create_index('document_id')
            mongo.db.extracted_data.create_index([('user_id', 1), ('document_id', 1)])
            
            print("✓ MongoDB indexes created successfully")
            
        except Exception as e:
            print(f"✗ Warning: Could not create indexes: {e}")
    
    return mongo
