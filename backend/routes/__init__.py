"""
Routes package initialization.
"""

from routes.auth import auth_bp
from routes.documents import documents_bp
from routes.chat import chat_bp
from routes.notifications import notifications_bp
from routes.user import user_bp
from routes.dashboard import dashboard_bp


def register_routes(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(documents_bp, url_prefix='/documents')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
