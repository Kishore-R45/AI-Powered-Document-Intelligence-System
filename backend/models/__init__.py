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
        """Initialize MongoDB connection with custom SSL context and retries."""
        mongo_uri = app.config['MONGO_URI']
        try:
            # Use certifi for SSL/TLS certificates on Windows
            import ssl as ssl_lib
            os.environ['SSL_CERT_FILE'] = certifi.where()
            
            # Create custom SSL context for Windows Python 3.10
            ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl_lib.CERT_NONE
            
            # PyMongo 4.x connection with better timeout settings and retries
            self.client = MongoClient(
                mongo_uri,
                tls=True,
                tlsAllowInvalidCertificates=True,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=10000,  # Reduced to 10s for faster failure
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                retryWrites=True,
                retryReads=True,
                maxPoolSize=50,
                minPoolSize=10,
            )
            
            # Get database name from URI or use default
            db_name = mongo_uri.split('/')[-1].split('?')[0] or 'infovault'
            self.db = self.client[db_name]
            
            # Test connection with retry
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
            print(f"  This could be due to:")
            print(f"  1. No internet connection")
            print(f"  2. MongoDB Atlas IP whitelist restrictions")
            print(f"  3. Firewall blocking MongoDB connections")
            print(f"  4. MongoDB Atlas cluster is paused")
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
