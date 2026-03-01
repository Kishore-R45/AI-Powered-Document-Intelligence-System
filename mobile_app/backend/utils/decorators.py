"""
Route decorators for authentication and error handling.
"""

from functools import wraps
from flask import request, jsonify, g
from utils.jwt_utils import JWTUtils
from models.user import User
from models.session import Session


def require_auth(f):
    """
    Decorator to require authentication for a route.
    Sets g.user_id, g.user, g.token_jti, and g.device_id if authentication succeeds.
    Also updates session last_active for auto-lock tracking.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Authorization header is required'}), 401
        
        token = JWTUtils.extract_token_from_header(auth_header)
        
        if not token:
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        # Decode token
        payload, error = JWTUtils.decode_token(token)
        
        if error:
            return jsonify({'error': error}), 401
        
        user_id = payload.get('sub')
        token_jti = payload.get('jti')
        device_id = payload.get('device_id')
        
        if not user_id:
            return jsonify({'error': 'Invalid token payload'}), 401
        
        # Check if session is revoked
        if token_jti and not Session.is_valid(token_jti):
            return jsonify({'error': 'Session has been revoked'}), 401
        
        # Update session last_active timestamp
        if token_jti:
            Session.update_last_active(token_jti)
        
        # Verify user exists and is active
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        if not user.get('is_active'):
            return jsonify({'error': 'Account is not activated'}), 401
        
        # Set user info in flask g object
        g.user_id = user_id
        g.user = user
        g.token_jti = token_jti
        g.device_id = device_id
        
        return f(*args, **kwargs)
    
    return decorated


def handle_errors(f):
    """
    Decorator to handle exceptions and return consistent JSON errors.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except FileNotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            print(f"Internal error in {f.__name__}: {e}")
            return jsonify({'error': 'An internal error occurred. Please try again.'}), 500
    
    return decorated


def optional_auth(f):
    """
    Decorator for routes that can optionally use authentication.
    Sets g.user_id and g.user if token is provided and valid, otherwise None.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        g.user_id = None
        g.user = None
        g.token_jti = None
        g.device_id = None
        
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            token = JWTUtils.extract_token_from_header(auth_header)
            
            if token:
                payload, error = JWTUtils.decode_token(token)
                
                if payload:
                    user_id = payload.get('sub')
                    token_jti = payload.get('jti')
                    device_id = payload.get('device_id')
                    
                    if user_id:
                        user = User.find_by_id(user_id)
                        if user and user.get('is_active'):
                            if not token_jti or Session.is_valid(token_jti):
                                g.user_id = user_id
                                g.user = user
                                g.token_jti = token_jti
                                g.device_id = device_id
        
        return f(*args, **kwargs)
    
    return decorated
