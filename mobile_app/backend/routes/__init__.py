"""
Routes package initialization for mobile app backend.
"""

from flask import Blueprint


def register_routes(app):
    """Register all route blueprints."""
    from routes.auth import auth_bp
    from routes.documents import documents_bp
    from routes.chat import chat_bp
    from routes.dashboard import dashboard_bp
    from routes.notifications import notifications_bp
    from routes.user import user_bp
    
    # Register blueprints with /api prefix
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(user_bp, url_prefix='/api/user')
