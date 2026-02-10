"""
Authentication routes.
Handles signup, login, OTP verification, and logout.
"""

from flask import Blueprint, request, jsonify, g
from models.user import User
from models.otp import OTP
from models.session import Session
from models.audit_log import AuditLog
from services.email_service import EmailService
from services.captcha_service import CaptchaService
from utils.validators import Validators
from utils.jwt_utils import JWTUtils
from utils.decorators import require_auth, handle_errors
from utils.responses import success_response, error_response

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
@handle_errors
def signup():
    """
    Register a new user.
    
    Request body:
        - name: User's full name
        - email: User's email address
        - password: User's password
        
    Response:
        - message: Success message
        - requiresOTP: True (email verification required)
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Validate inputs
    valid, error = Validators.validate_name(name)
    if not valid:
        return error_response(error, 400)
    
    valid, error = Validators.validate_email(email)
    if not valid:
        return error_response(error, 400)
    
    valid, error = Validators.validate_password(password)
    if not valid:
        return error_response(error, 400)
    
    # Check if user already exists
    if User.exists(email):
        existing_user = User.find_by_email(email)
        if existing_user and existing_user.get('is_active'):
            return error_response("An account with this email already exists", 409)
        else:
            # User exists but not activated - allow re-registration
            # Delete old user and OTPs
            from models import mongo
            mongo.db.users.delete_one({'email': email})
            OTP.delete_for_email(email)
    
    # Create user (inactive until OTP verification)
    user = User.create(name=name, email=email, password=password, is_active=False)
    
    # Generate and send OTP
    otp = OTP.create(email)
    email_sent = EmailService.send_otp(email, otp['code'], name)
    
    if not email_sent:
        # Clean up user if email fails
        from models import mongo
        mongo.db.users.delete_one({'_id': user['_id']})
        OTP.delete_for_email(email)
        return error_response("Failed to send verification email. Please try again.", 500)
    
    # Log signup attempt
    AuditLog.log(
        action=AuditLog.ACTION_SIGNUP,
        user_id=str(user['_id']),
        details={'email': email}
    )
    
    return success_response(
        message="Verification code sent to your email.",
        data={'requiresOTP': True, 'email': email},
        status_code=201
    )


@auth_bp.route('/verify-otp', methods=['POST'])
@handle_errors
def verify_otp():
    """
    Verify OTP and activate user account.
    
    Request body:
        - email: User's email address
        - otp: 6-digit OTP code
        - resend: (optional) If true, resend OTP instead of verifying
        
    Response:
        - token: JWT access token (if successful)
        - user: User data
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    email = data.get('email', '').strip().lower()
    otp_code = data.get('otp', '').strip()
    resend = data.get('resend', False)
    
    # Validate email
    valid, error = Validators.validate_email(email)
    if not valid:
        return error_response(error, 400)
    
    # Handle resend request
    if resend:
        user = User.find_by_email(email)
        if not user:
            return error_response("No account found with this email", 404)
        
        if user.get('is_active'):
            return error_response("Account is already verified", 400)
        
        # Generate new OTP
        otp = OTP.create(email)
        email_sent = EmailService.send_otp(email, otp['code'], user.get('name'))
        
        if not email_sent:
            return error_response("Failed to send verification email", 500)
        
        return success_response(message="New verification code sent to your email.")
    
    # Validate OTP
    valid, error = Validators.validate_otp(otp_code)
    if not valid:
        return error_response(error, 400)
    
    # Verify OTP
    success, message = OTP.verify(email, otp_code)
    
    if not success:
        return error_response(message, 400)
    
    # Activate user
    User.activate(email)
    user = User.find_by_email(email)
    
    if not user:
        return error_response("User not found", 404)
    
    # Generate tokens
    token, jti, expires_at = JWTUtils.generate_token(str(user['_id']), 'access')
    
    # Store session
    Session.create(str(user['_id']), jti, expires_at)
    
    return success_response(
        data={
            'token': token,
            'user': User.to_dict(user)
        },
        message="Email verified successfully."
    )


@auth_bp.route('/login', methods=['POST'])
@handle_errors
def login():
    """
    Login with email and password.
    
    Request body:
        - email: User's email address
        - password: User's password
        - captchaToken: (optional) reCAPTCHA token
        
    Response:
        - token: JWT access token
        - user: User data
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    captcha_token = data.get('captchaToken')
    
    # Validate inputs
    valid, error = Validators.validate_email(email)
    if not valid:
        return error_response(error, 400)
    
    if not password:
        return error_response("Password is required", 400)
    
    # Verify captcha (if configured)
    captcha_valid, captcha_error = CaptchaService.verify(
        captcha_token,
        request.remote_addr
    )
    if not captcha_valid:
        AuditLog.log(
            action=AuditLog.ACTION_LOGIN_FAILED,
            details={'email': email, 'reason': 'captcha_failed'}
        )
        return error_response(captcha_error, 400)
    
    # Find user
    user = User.find_by_email(email)
    
    if not user:
        AuditLog.log(
            action=AuditLog.ACTION_LOGIN_FAILED,
            details={'email': email, 'reason': 'user_not_found'}
        )
        return error_response("Invalid email or password", 401)
    
    # Check if account is active
    if not user.get('is_active'):
        AuditLog.log(
            action=AuditLog.ACTION_LOGIN_FAILED,
            user_id=str(user['_id']),
            details={'reason': 'account_inactive'}
        )
        return error_response("Please verify your email before logging in", 401)
    
    # Verify password
    if not User.verify_password(user, password):
        AuditLog.log(
            action=AuditLog.ACTION_LOGIN_FAILED,
            user_id=str(user['_id']),
            details={'reason': 'invalid_password'}
        )
        return error_response("Invalid email or password", 401)
    
    # Generate tokens
    token, jti, expires_at = JWTUtils.generate_token(str(user['_id']), 'access')
    
    # Store session
    Session.create(str(user['_id']), jti, expires_at)
    
    # Log successful login
    AuditLog.log(
        action=AuditLog.ACTION_LOGIN,
        user_id=str(user['_id']),
        details={'email': email}
    )
    
    return success_response(
        data={
            'token': token,
            'user': User.to_dict(user)
        }
    )


@auth_bp.route('/logout', methods=['POST'])
@require_auth
@handle_errors
def logout():
    """
    Logout current session.
    Revokes the current JWT token.
    """
    # Revoke current session
    if g.token_jti:
        Session.revoke(g.token_jti)
    
    # Log logout
    AuditLog.log(
        action=AuditLog.ACTION_LOGOUT,
        user_id=g.user_id
    )
    
    return success_response(message="Logged out successfully.")


@auth_bp.route('/refresh', methods=['POST'])
@require_auth
@handle_errors
def refresh():
    """
    Refresh the access token.
    
    Response:
        - token: New JWT access token
    """
    # Revoke old session
    if g.token_jti:
        Session.revoke(g.token_jti)
    
    # Generate new token
    token, jti, expires_at = JWTUtils.generate_token(g.user_id, 'access')
    
    # Store new session
    Session.create(g.user_id, jti, expires_at)
    
    return success_response(data={'token': token})
