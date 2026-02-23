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
        - captchaToken: (optional) reCAPTCHA token
        
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
    captcha_token = data.get('captchaToken', '')
    
    # Verify captcha (skips automatically for localhost)
    captcha_valid, captcha_error = CaptchaService.verify(captcha_token, request.remote_addr)
    if not captcha_valid:
        print(f"[Signup] Captcha failed for {email}: {captcha_error}")
        return error_response(captcha_error or "Captcha verification failed", 400)
    
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
    try:
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
    except Exception as e:
        print(f"[Signup] Error checking existing user: {e}")
        return error_response("Database error during registration. Please try again.", 500)
    
    # Create user (inactive until OTP verification)
    try:
        user = User.create(name=name, email=email, password=password, is_active=False)
    except Exception as e:
        print(f"[Signup] Error creating user: {e}")
        import traceback
        traceback.print_exc()
        return error_response("Failed to create account. Please try again.", 500)
    
    # Generate and send OTP
    try:
        otp = OTP.create(email)
        email_sent = EmailService.send_otp(email, otp['code'], name)
        
        if not email_sent:
            print(f"[Signup] Failed to send OTP email to {email}")
            # Clean up user if email fails
            from models import mongo
            mongo.db.users.delete_one({'_id': user['_id']})
            OTP.delete_for_email(email)
            return error_response("Failed to send verification email. Please check your email address and try again.", 500)
    except Exception as e:
        print(f"[Signup] Error in OTP/email flow: {e}")
        import traceback
        traceback.print_exc()
        # Clean up user if OTP/email fails
        from models import mongo
        try:
            mongo.db.users.delete_one({'_id': user['_id']})
        except:
            pass
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
    
    # Store session with device info (first login after signup - establishes known device)
    client_ip = request.remote_addr
    client_ua = request.user_agent.string if request.user_agent else None
    Session.create(str(user['_id']), jti, expires_at, ip_address=client_ip, user_agent=client_ua)
    
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
    
    # Get client info for session tracking
    client_ip = request.remote_addr
    client_ua = request.user_agent.string if request.user_agent else None
    
    # Check if login is from a new device (skip for newly registered accounts)
    is_new = Session.is_new_device(str(user['_id']), client_ip, client_ua)
    
    # Store session with device info
    Session.create(str(user['_id']), jti, expires_at, ip_address=client_ip, user_agent=client_ua)
    
    # Send new device login alert email (only for existing accounts, not first login)
    if is_new:
        try:
            EmailService.send_login_alert(
                to_email=email,
                name=user.get('name'),
                ip_address=client_ip,
                user_agent=client_ua
            )
            print(f"[Auth] New device login alert sent to {email}")
        except Exception as e:
            print(f"[Auth] Failed to send login alert: {e}")
    
    # Log successful login
    AuditLog.log(
        action=AuditLog.ACTION_LOGIN,
        user_id=str(user['_id']),
        details={'email': email, 'new_device': is_new}
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
    
    # Store new session with device info
    client_ip = request.remote_addr
    client_ua = request.user_agent.string if request.user_agent else None
    Session.create(g.user_id, jti, expires_at, ip_address=client_ip, user_agent=client_ua)
    
    return success_response(data={'token': token})


@auth_bp.route('/forgot-password', methods=['POST'])
@handle_errors
def forgot_password():
    """
    Initiate forgot password flow.
    Sends OTP to the registered email address.
    
    Request body:
        - email: User's email address
        
    Response:
        - message: Success message
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    email = data.get('email', '').strip().lower()
    
    # Validate email
    valid, error = Validators.validate_email(email)
    if not valid:
        return error_response(error, 400)
    
    # Find user
    user = User.find_by_email(email)
    
    if not user:
        # Don't reveal whether email exists (security best practice)
        return success_response(message="If an account with that email exists, a verification code has been sent.")
    
    if not user.get('is_active'):
        return error_response("Account is not verified. Please sign up again.", 400)
    
    # Generate and send OTP
    otp = OTP.create(email)
    email_sent = EmailService.send_otp(email, otp['code'], user.get('name'))
    
    if not email_sent:
        return error_response("Failed to send verification email. Please try again.", 500)
    
    return success_response(message="If an account with that email exists, a verification code has been sent.")


@auth_bp.route('/verify-reset-otp', methods=['POST'])
@handle_errors
def verify_reset_otp():
    """
    Verify OTP for password reset.
    
    Request body:
        - email: User's email address
        - otp: 6-digit OTP code
        - resend: (optional) If true, resend OTP instead of verifying
        
    Response:
        - message: Success message
        - resetToken: Token to authorize password reset
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
    
    # Generate a short-lived reset token
    user = User.find_by_email(email)
    if not user:
        return error_response("User not found", 404)
    
    reset_token, _, _ = JWTUtils.generate_token(str(user['_id']), 'access', expires_minutes=15)
    
    return success_response(
        message="OTP verified successfully. You can now reset your password.",
        data={'resetToken': reset_token, 'email': email}
    )


@auth_bp.route('/reset-password', methods=['POST'])
@handle_errors
def reset_password():
    """
    Reset password after OTP verification.
    
    Request body:
        - email: User's email address
        - resetToken: Token from verify-reset-otp
        - newPassword: New password
        
    Response:
        - message: Success message
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    email = data.get('email', '').strip().lower()
    reset_token = data.get('resetToken', '')
    new_password = data.get('newPassword', '')
    
    # Validate email
    valid, error = Validators.validate_email(email)
    if not valid:
        return error_response(error, 400)
    
    # Validate new password
    valid, error = Validators.validate_password(new_password)
    if not valid:
        return error_response(error, 400)
    
    # Verify the reset token
    payload, token_error = JWTUtils.decode_token(reset_token)
    if not payload or token_error:
        return error_response("Invalid or expired reset token. Please start the process again.", 400)
    token_user_id = payload.get('sub')
    
    # Find user
    user = User.find_by_email(email)
    if not user:
        return error_response("User not found", 404)
    
    # Verify token belongs to this user
    if str(user['_id']) != token_user_id:
        return error_response("Invalid reset token", 400)
    
    # Update password
    User.update_password(str(user['_id']), new_password)
    
    # Revoke all existing sessions
    Session.revoke_all_for_user(str(user['_id']))
    
    # Log password change
    AuditLog.log(
        action=AuditLog.ACTION_PASSWORD_CHANGE,
        user_id=str(user['_id']),
        details={'method': 'forgot_password'}
    )
    
    # Send password changed notification
    EmailService.send_password_changed(email, user.get('name'))
    
    return success_response(message="Password reset successfully. Please login with your new password.")
