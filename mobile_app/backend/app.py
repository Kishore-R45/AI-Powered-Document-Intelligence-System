"""
InfoVault Mobile Backend Application
Separate Flask backend for the mobile app.

Features:
- Biometric authentication with trusted devices
- Firebase Cloud Messaging push notifications
- AI key-value data extraction from documents
- Offline-friendly: no S3, documents stored locally on device
- Extended JWT sessions (30d access, 90d refresh, 365d biometric)
- Auto-lock after 5 minutes of inactivity
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import init_db
from routes import register_routes


def create_app():
    """Application factory function."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Configure CORS (allow all for mobile)
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)
    
    # Initialize database
    init_db(app)
    
    # Initialize Firebase
    print("[Init] Initializing Firebase...")
    try:
        from services.firebase_service import FirebaseService
        FirebaseService.initialize()
        print("✓ Firebase initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize Firebase: {e}")
        print("  Push notifications will be unavailable")
    
    # Pre-load embedding model
    print("[Init] Pre-loading embedding model...")
    try:
        from services.embedding_service import EmbeddingService
        EmbeddingService.get_model()
        print("✓ Embedding model pre-loaded successfully")
    except Exception as e:
        print(f"✗ Failed to pre-load embedding model: {e}")
        print("  Model will be loaded on first use")
    
    # Register blueprints
    register_routes(app)
    
    # Health check
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'infovault-mobile-api'
        }), 200
    
    # Root
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'name': 'InfoVault Mobile API',
            'version': '1.0.0',
            'status': 'running',
            'features': [
                'biometric_auth',
                'push_notifications',
                'data_extraction',
                'offline_support',
                'document_chat'
            ]
        }), 200
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden', 'message': 'Access denied'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed'}), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({'error': 'File too large', 'message': 'Maximum file size is 15MB'}), 413
    
    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({'error': 'Too many requests', 'message': 'Please slow down'}), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
    
    return app


def init_scheduler(app):
    """
    Initialize background job scheduler.
    Runs expiry checks with both email and push notifications.
    """
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from jobs.expiry_reminder import ExpiryReminderJob
    
    scheduler = BackgroundScheduler()
    
    def keep_alive():
        """Ping health endpoint to prevent HuggingFace Spaces sleep."""
        import requests, os
        space_url = os.getenv('SPACE_HOST')
        port = int(os.getenv('PORT', 7860))
        
        if space_url:
            url = f"https://{space_url}/health"
        else:
            url = f"http://localhost:{port}/health"
        
        try:
            resp = requests.get(url, timeout=15)
            print(f"[KeepAlive] Ping {url} → {resp.status_code}")
        except Exception as e:
            print(f"[KeepAlive] Ping failed: {e}")
    
    def run_with_context():
        """Run expiry reminder within Flask app context."""
        with app.app_context():
            try:
                ExpiryReminderJob.run()
            except Exception as e:
                print(f"Error running expiry reminder job: {e}")
    
    def check_expired_with_context():
        with app.app_context():
            try:
                ExpiryReminderJob.check_expired()
            except Exception as e:
                print(f"Error running expired check job: {e}")
    
    # Keep-alive every 14 minutes
    scheduler.add_job(
        func=keep_alive,
        trigger=IntervalTrigger(minutes=14),
        id='keep_alive_ping',
        name='Keep alive ping',
        replace_existing=True
    )
    
    # Expiry reminder every 6 hours
    scheduler.add_job(
        func=run_with_context,
        trigger=IntervalTrigger(hours=6),
        id='expiry_reminder_job',
        name='Check document expiry and send reminders + push',
        replace_existing=True
    )
    
    # Daily at 8 AM UTC
    scheduler.add_job(
        func=run_with_context,
        trigger=CronTrigger(hour=8, minute=0),
        id='expiry_reminder_daily_job',
        name='Daily expiry reminder check',
        replace_existing=True
    )
    
    # Expired check daily at 9 AM UTC
    scheduler.add_job(
        func=check_expired_with_context,
        trigger=CronTrigger(hour=9, minute=0),
        id='expired_check_job',
        name='Check for expired documents',
        replace_existing=True
    )
    
    scheduler.start()
    
    # Run once on startup
    import threading
    def startup_check():
        import time
        time.sleep(5)
        run_with_context()
    
    startup_thread = threading.Thread(target=startup_check, daemon=True)
    startup_thread.start()
    
    import atexit
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler


# Create the application
app = create_app()

# Initialize scheduler
try:
    _scheduler = init_scheduler(app)
    print("✓ Background scheduler initialized")
except Exception as e:
    print(f"✗ Failed to initialize scheduler: {e}")


if __name__ == '__main__':
    import os
    
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    port = int(os.getenv('PORT', 7860))
    host = os.getenv('HOST', '0.0.0.0')
    
    app.run(host=host, port=port, debug=debug)
