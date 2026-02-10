"""
WSGI entry point for production deployment.
"""

from app import app, init_scheduler
import os

# Initialize scheduler for production
if os.getenv('FLASK_ENV') == 'production':
    init_scheduler(app)

if __name__ == '__main__':
    app.run()
