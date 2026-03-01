"""
Authentication routes for mobile app.
Handles signup, login, OTP, biometric login, trusted devices, and session management.
No captcha for mobile - uses device ID tracking instead.
"""

from flask import Blueprint, request, jsonify, g
from models.user import User
from models.otp import OTP
from models.session import Session
from models.audit_log import AuditLog
from models.trusted_device import TrustedDevice
from services.email_service import EmailService
from utils.validators import Validators
from utils.jwt_utils import JWTUtils
from utils.decorators import require_auth, handle_errors
from utils.responses import success_response, error_response

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
@handle_errors
def signup():
    """Register a new user (mobile - no captcha)."""
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
    
    # Check existing user
    try:
        if User.exists(email):
            existing_user = User.find_by_email(email)
            if existing_user and existing_user.get('is_active'):
                return error_response("An account with this email already exists", 409)
            else:
                from models import mongo
                mongo.db.users.delete_one({'email': email})
                OTP.delete_for_email(email)
    except Exception as e:
        print(f"[Signup] Error checking existing user: {e}")
        return error_response("Database error. Please try again.", 500)
    
    # Create user (inactive until OTP)
    try:
        user = User.create(name=name, email=email, password=password, is_active=False)
    except Exception as e:
        print(f"[Signup] Error creating user: {e}")
        return error_response("Failed to create account. Please try again.", 500)
    
    # Generate and send OTP
    try:
        otp = OTP.create(email)
        email_sent = EmailService.send_otp(email, otp['code'], name)
        
        if not email_sent:
            from models import mongo
            mongo.db.users.delete_one({'_id': user['_id']})
            OTP.delete_for_email(email)
            return error_response("Failed to send verification email.", 500)
    except Exception as e:
        from models import mongo
        try:
            mongo.db.users.delete_one({'_id': user['_id']})
        except:
            pass
        return error_response("Failed to send verification email.", 500)
    
    AuditLog.log(action=AuditLog.ACTION_SIGNUP, user_id=str(user['_id']), details={'email': email})
    
    return success_response(
        message="Verification code sent to your email.",
        data={'requiresOTP': True, 'email': email},
        status_code=201
    )


@auth_bp.route('/verify-otp', methods=['POST'])
@handle_errors
def verify_otp():
    """Verify OTP and activate user account."""
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    email = data.get('email', '').strip().lower()
    otp_code = data.get('otp', '').strip()
    resend = data.get('resend', False)
    device_id = data.get('deviceId', '')
    
    valid, error = Validators.validate_email(email)
    if not valid:
        return error_response(error, 400)
    
    # Handle resend
    if resend:
        user = User.find_by_email(email)
        if not user:
            return error_response("No account found with this email", 404)
        if user.get('is_active'):
            return error_response("Account is already verified", 400)
        
        otp = OTP.create(email)
        email_sent = EmailService.send_otp(email, otp['code'], user.get('name'))
        if not email_sent:
            return error_response("Failed to send verification email", 500)
        
        return success_response(message="New verification code sent to your email.")
    
    # Validate OTP
    valid, error = Validators.validate_otp(otp_code)
    if not valid:
        return error_response(error, 400)
    
    success, message = OTP.verify(email, otp_code)
    if not success:
        return error_response(message, 400)
    
    # Activate user
    User.activate(email)
    user = User.find_by_email(email)
    if not user:
        return error_response("User not found", 404)
    
    # Generate token with device info
    token, jti, expires_at = JWTUtils.generate_token(
        str(user['_id']), 'access', device_id=device_id
    )
    
    client_ip = request.remote_addr
    client_ua = request.headers.get('User-Agent', '')
    Session.create(
        str(user['_id']), jti, expires_at,
        ip_address=client_ip, user_agent=client_ua,
        device_id=device_id, session_type=Session.SESSION_TYPE_STANDARD
    )
    
    return success_response(
        data={'token': token, 'user': User.to_dict(user)},
        message="Email verified successfully."
    )


@auth_bp.route('/login', methods=['POST'])
@handle_errors
def login():
    """Login with email and password (mobile - no captcha)."""
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    device_id = data.get('deviceId', '')
    device_name = data.get('deviceName', '')
    
    valid, error = Validators.validate_email(email)
    if not valid:
        return error_response(error, 400)
    
    if not password:
        return error_response("Password is required", 400)
    
    # Find and verify user
    user = User.find_by_email(email)
    if not user:
        AuditLog.log(action=AuditLog.ACTION_LOGIN_FAILED, details={'email': email, 'reason': 'user_not_found'})
        return error_response("Invalid email or password", 401)
    
    if not user.get('is_active'):
        return error_response("Please verify your email before logging in", 401)
    
    if not User.verify_password(user, password):
        AuditLog.log(action=AuditLog.ACTION_LOGIN_FAILED, user_id=str(user['_id']), details={'reason': 'invalid_password'})
        return error_response("Invalid email or password", 401)
    
    # Generate token
    token, jti, expires_at = JWTUtils.generate_token(
        str(user['_id']), 'access', device_id=device_id
    )
    
    client_ip = request.remote_addr
    client_ua = request.headers.get('User-Agent', '')
    
    # Check for new device
    is_new = Session.is_new_device(str(user['_id']), client_ip, client_ua)
    
    Session.create(
        str(user['_id']), jti, expires_at,
        ip_address=client_ip, user_agent=client_ua,
        device_id=device_id, session_type=Session.SESSION_TYPE_STANDARD
    )
    
    # Send new device login alert
    if is_new:
        try:
            EmailService.send_login_alert(email, user.get('name'), client_ip, client_ua)
        except Exception as e:
            print(f"[Auth] Failed to send login alert: {e}")
    
    AuditLog.log(
        action=AuditLog.ACTION_LOGIN,
        user_id=str(user['_id']),
        details={'email': email, 'new_device': is_new, 'device_id': device_id}
    )
    
    # Check if biometric is enabled for this device
    biometric_available = False
    if device_id and user.get('biometric_enabled'):
        biometric_available = TrustedDevice.is_trusted(str(user['_id']), device_id)
    
    return success_response(data={
        'token': token,
        'user': User.to_dict(user),
        'biometricAvailable': biometric_available,
    })


@auth_bp.route('/biometric-login', methods=['POST'])
@handle_errors
def biometric_login():
    """
    Login using biometric authentication.
    The device must be previously registered as a trusted device.
    Client-side biometric verification is done by the mobile app using local_auth.
    This endpoint validates the device is trusted and issues a long-lived token.
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    device_id = data.get('deviceId', '')
    user_id = data.get('userId', '')
    
    if not device_id:
        return error_response("Device ID is required", 400)
    if not user_id:
        return error_response("User ID is required", 400)
    
    # Verify device is trusted
    if not TrustedDevice.is_trusted(user_id, device_id):
        return error_response("Device is not registered for biometric login", 401)
    
    # Verify user exists and is active
    user = User.find_by_id(user_id)
    if not user:
        return error_response("User not found", 401)
    if not user.get('is_active'):
        return error_response("Account is not activated", 401)
    if not user.get('biometric_enabled'):
        return error_response("Biometric login is not enabled", 401)
    
    # Update device last used
    TrustedDevice.update_last_used(user_id, device_id)
    
    # Generate long-lived biometric token
    token, jti, expires_at = JWTUtils.generate_token(
        user_id, 'access', device_id=device_id, session_type='biometric'
    )
    
    client_ip = request.remote_addr
    client_ua = request.headers.get('User-Agent', '')
    
    Session.create(
        user_id, jti, expires_at,
        ip_address=client_ip, user_agent=client_ua,
        device_id=device_id, session_type=Session.SESSION_TYPE_BIOMETRIC
    )
    
    AuditLog.log(
        action=AuditLog.ACTION_BIOMETRIC_LOGIN,
        user_id=user_id,
        details={'device_id': device_id}
    )
    
    return success_response(data={
        'token': token,
        'user': User.to_dict(user),
    })


@auth_bp.route('/register-device', methods=['POST'])
@require_auth
@handle_errors
def register_device():
    """
    Register a device as trusted for biometric login.
    Requires user to be authenticated (after successful password login).
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    device_id = data.get('deviceId', '')
    device_name = data.get('deviceName', 'Unknown Device')
    device_model = data.get('deviceModel', '')
    os_version = data.get('osVersion', '')
    biometric_type = data.get('biometricType', 'fingerprint')
    
    valid, error = Validators.validate_device_id(device_id)
    if not valid:
        return error_response(error, 400)
    
    # Register the device
    device = TrustedDevice.register(
        user_id=g.user_id,
        device_id=device_id,
        device_name=device_name,
        device_model=device_model,
        os_version=os_version,
        biometric_type=biometric_type
    )
    
    # Enable biometric for user
    User.enable_biometric(g.user_id, device_id)
    
    AuditLog.log(
        action=AuditLog.ACTION_BIOMETRIC_ENABLE,
        user_id=g.user_id,
        details={'device_id': device_id, 'device_name': device_name}
    )
    
    return success_response(
        data={'device': TrustedDevice.to_dict(device)},
        message="Device registered for biometric login."
    )


@auth_bp.route('/validate-session', methods=['POST'])
@require_auth
@handle_errors
def validate_session():
    """
    Validate if the current session is still active.
    Used by mobile app to check session validity for offline/online transitions.
    Also updates last_active timestamp.
    """
    user = User.find_by_id(g.user_id)
    if not user:
        return error_response("User not found", 401)
    
    return success_response(data={
        'valid': True,
        'user': User.to_dict(user),
    })


@auth_bp.route('/logout', methods=['POST'])
@require_auth
@handle_errors
def logout():
    """Logout current session."""
    if g.token_jti:
        Session.revoke(g.token_jti)
    
    AuditLog.log(action=AuditLog.ACTION_LOGOUT, user_id=g.user_id)
    
    return success_response(message="Logged out successfully.")


@auth_bp.route('/refresh', methods=['POST'])
@require_auth
@handle_errors
def refresh():
    """Refresh the access token."""
    device_id = g.device_id or ''
    
    if g.token_jti:
        Session.revoke(g.token_jti)
    
    token, jti, expires_at = JWTUtils.generate_token(
        g.user_id, 'access', device_id=device_id
    )
    
    client_ip = request.remote_addr
    client_ua = request.headers.get('User-Agent', '')
    Session.create(
        g.user_id, jti, expires_at,
        ip_address=client_ip, user_agent=client_ua,
        device_id=device_id, session_type=Session.SESSION_TYPE_STANDARD
    )
    
    return success_response(data={'token': token})


@auth_bp.route('/forgot-password', methods=['POST'])
@handle_errors
def forgot_password():
    """Initiate forgot password flow."""
    data = request.get_json()
    if not data:
        return error_response("Request body is required", 400)
    
    email = data.get('email', '').strip().lower()
    
    valid, error = Validators.validate_email(email)
    if not valid:
        return error_response(error, 400)
    
    user = User.find_by_email(email)
    if not user:
        return success_response(message="If an account with that email exists, a verification code has been sent.")
    
    if not user.get('is_active'):
        return error_response("Account is not verified. Please sign up again.", 400)
    
    otp = OTP.create(email)
    email_sent = EmailService.send_otp(email, otp['code'], user.get('name'))
    if not email_sent:
        return error_response("Failed to send verification email.", 500)
    
    return success_response(message="If an account with that email exists, a verification code has been sent.")


@auth_bp.route('/verify-reset-otp', methods=['POST'])
@handle_errors
def verify_reset_otp():
    """Verify OTP for password reset."""
    data = request.get_json()
    if not data:
        return error_response("Request body is required", 400)
    
    email = data.get('email', '').strip().lower()
    otp_code = data.get('otp', '').strip()
    resend = data.get('resend', False)
    
    valid, error = Validators.validate_email(email)
    if not valid:
        return error_response(error, 400)
    
    if resend:
        user = User.find_by_email(email)
        if not user:
            return error_response("No account found with this email", 404)
        otp = OTP.create(email)
        email_sent = EmailService.send_otp(email, otp['code'], user.get('name'))
        if not email_sent:
            return error_response("Failed to send verification email", 500)
        return success_response(message="New verification code sent to your email.")
    
    valid, error = Validators.validate_otp(otp_code)
    if not valid:
        return error_response(error, 400)
    
    success, message = OTP.verify(email, otp_code)
    if not success:
        return error_response(message, 400)
    
    user = User.find_by_email(email)
    if not user:
        return error_response("User not found", 404)
    
    reset_token, _, _ = JWTUtils.generate_token(str(user['_id']), 'access', expires_minutes=15)
    
    return success_response(
        message="OTP verified successfully.",
        data={'resetToken': reset_token, 'email': email}
    )


@auth_bp.route('/reset-password', methods=['POST'])
@handle_errors
def reset_password():
    """Reset password after OTP verification."""
    data = request.get_json()
    if not data:
        return error_response("Request body is required", 400)
    
    email = data.get('email', '').strip().lower()
    reset_token = data.get('resetToken', '')
    new_password = data.get('newPassword', '')
    
    valid, error = Validators.validate_email(email)
    if not valid:
        return error_response(error, 400)
    
    valid, error = Validators.validate_password(new_password)
    if not valid:
        return error_response(error, 400)
    
    payload, token_error = JWTUtils.decode_token(reset_token)
    if not payload or token_error:
        return error_response("Invalid or expired reset token.", 400)
    
    user = User.find_by_email(email)
    if not user:
        return error_response("User not found", 404)
    
    if str(user['_id']) != payload.get('sub'):
        return error_response("Invalid reset token", 400)
    
    User.update_password(str(user['_id']), new_password)
    Session.revoke_all_for_user(str(user['_id']))
    
    AuditLog.log(
        action=AuditLog.ACTION_PASSWORD_CHANGE,
        user_id=str(user['_id']),
        details={'method': 'forgot_password'}
    )
    
    EmailService.send_password_changed(email, user.get('name'))
    
    return success_response(message="Password reset successfully. Please login with your new password.")
