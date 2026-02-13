"""
InfoVault Backend Application
Enterprise-grade personal document management system.

Main Flask application entry point.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import get_config
from models import init_db
from routes import register_routes


def create_app(config_class=None):
    """
    Application factory function.
    
    Args:
        config_class: Configuration class to use (optional)
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)
    
    # Configure CORS
    CORS(app, origins=config_class.CORS_ORIGINS, supports_credentials=True)
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    register_routes(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for load balancers."""
        return jsonify({
            'status': 'healthy',
            'service': 'infovault-api'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """API root endpoint."""
        return jsonify({
            'name': 'InfoVault API',
            'version': '1.0.0',
            'status': 'running'
        }), 200
    
    # Global error handlers
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
        return jsonify({'error': 'File too large', 'message': 'Maximum file size is 10MB'}), 413
    
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
    
    Args:
        app: Flask application
    """
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from jobs.expiry_reminder import ExpiryReminderJob
    
    scheduler = BackgroundScheduler()
    
    # Run expiry reminder job daily at 8 AM UTC
    scheduler.add_job(
        func=ExpiryReminderJob.run,
        trigger=CronTrigger(hour=8, minute=0),
        id='expiry_reminder_job',
        name='Check document expiry and send reminders',
        replace_existing=True
    )
    
    # Run expired check daily at 9 AM UTC
    scheduler.add_job(
        func=ExpiryReminderJob.check_expired,
        trigger=CronTrigger(hour=9, minute=0),
        id='expired_check_job',
        name='Check for expired documents',
        replace_existing=True
    )
    
    scheduler.start()
    
    # Shut down the scheduler when the app is shutting down
    import atexit
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler


# Create the application
app = create_app()


if __name__ == '__main__':
    import os
    
    # Initialize scheduler in production
    if os.getenv('FLASK_ENV') == 'production':
        init_scheduler(app)
    
    # Run the application
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    # Default to 7860 for Hugging Face Spaces, fallback to 5000
    port = int(os.getenv('PORT', 7860))
    host = os.getenv('HOST', '0.0.0.0')
    
    app.run(host=host, port=port, debug=debug)
