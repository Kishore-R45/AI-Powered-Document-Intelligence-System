"""
WSGI entry point for production deployment.
Scheduler is automatically initialized in app.py.
"""

from app import app

if __name__ == '__main__':
    app.run()
