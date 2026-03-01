"""
User profile and account routes for mobile app.
Includes biometric toggle, session management, and trusted device management.
"""

from flask import Blueprint, request, g

from models.user import User
from models.session import Session
from models.trusted_device import TrustedDevice
from models.audit_log import AuditLog
from services.email_service import EmailService
from utils.validators import Validators
from utils.decorators import require_auth, handle_errors
from utils.responses import success_response, error_response

user_bp = Blueprint('user', __name__)


@user_bp.route('/profile', methods=['GET'])
@require_auth
@handle_errors
def get_profile():
    """Get current user's profile."""
    return success_response(data={
        'user': User.to_dict(g.user)
    })


@user_bp.route('/profile', methods=['PUT', 'PATCH'])
@require_auth
@handle_errors
def update_profile():
    """Update current user's profile."""
    data = request.get_json() or {}
    update_fields = {}
    
    if 'name' in data:
        valid, error = Validators.validate_name(data['name'])
        if not valid:
            return error_response(error, 400)
        update_fields['name'] = Validators.sanitize_string(data['name'], 100)
    
    if update_fields:
        User.update(g.user_id, update_fields)
        AuditLog.log(
            action=AuditLog.ACTION_PROFILE_UPDATE,
            user_id=g.user_id,
            details={'updated_fields': list(update_fields.keys())}
        )
    
    updated_user = User.find_by_id(g.user_id)
    
    return success_response(
        data={'user': User.to_dict(updated_user)},
        message="Profile updated successfully."
    )


@user_bp.route('/change-password', methods=['POST'])
@require_auth
@handle_errors
def change_password():
    """Change current user's password."""
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    current_password = data.get('currentPassword', '')
    new_password = data.get('newPassword', '')
    
    if not current_password:
        return error_response("Current password is required", 400)
    
    valid, error = Validators.validate_password(new_password)
    if not valid:
        return error_response(error, 400)
    
    if not User.verify_password(g.user, current_password):
        return error_response("Current password is incorrect", 401)
    
    if current_password == new_password:
        return error_response("New password must be different from current password", 400)
    
    User.update_password(g.user_id, new_password)
    Session.revoke_all_for_user(g.user_id)
    
    AuditLog.log(
        action=AuditLog.ACTION_PASSWORD_CHANGE,
        user_id=g.user_id
    )
    
    EmailService.send_password_changed(g.user['email'], g.user.get('name'))
    
    return success_response(message="Password changed successfully.")


@user_bp.route('/logout-all', methods=['POST'])
@require_auth
@handle_errors
def logout_all():
    """Logout from all sessions/devices."""
    count = Session.revoke_all_for_user(g.user_id)
    
    AuditLog.log(
        action=AuditLog.ACTION_SESSION_LOGOUT_ALL,
        user_id=g.user_id,
        details={'sessions_revoked': count}
    )
    
    return success_response(
        message="Logged out from all sessions.",
        data={'count': count}
    )


# ---- Biometric Endpoints ----

@user_bp.route('/biometric/toggle', methods=['POST'])
@require_auth
@handle_errors
def toggle_biometric():
    """
    Enable or disable biometric login for the user.
    When disabling, revokes all trusted devices.
    """
    data = request.get_json()
    if not data:
        return error_response("Request body is required", 400)
    
    enabled = data.get('enabled', False)
    device_id = data.get('deviceId', '')
    
    if enabled:
        if not device_id:
            return error_response("Device ID is required to enable biometric", 400)
        
        User.enable_biometric(g.user_id, device_id)
        
        AuditLog.log(
            action=AuditLog.ACTION_BIOMETRIC_ENABLE,
            user_id=g.user_id,
            details={'device_id': device_id}
        )
        
        return success_response(message="Biometric login enabled.")
    else:
        User.disable_biometric(g.user_id)
        TrustedDevice.revoke_all(g.user_id)
        
        AuditLog.log(
            action=AuditLog.ACTION_BIOMETRIC_DISABLE,
            user_id=g.user_id
        )
        
        return success_response(message="Biometric login disabled. All trusted devices removed.")


@user_bp.route('/biometric/status', methods=['GET'])
@require_auth
@handle_errors
def biometric_status():
    """Get biometric login status for the current user."""
    user = User.find_by_id(g.user_id)
    devices = TrustedDevice.get_user_devices(g.user_id)
    
    return success_response(data={
        'enabled': user.get('biometric_enabled', False),
        'trustedDevices': [TrustedDevice.to_dict(d) for d in devices],
    })


# ---- Session Endpoints ----

@user_bp.route('/sessions', methods=['GET'])
@require_auth
@handle_errors
def list_sessions():
    """List all active sessions for the current user."""
    sessions = Session.find_active_by_user(g.user_id)
    
    session_list = []
    for s in sessions:
        session_list.append({
            'id': str(s['_id']),
            'deviceId': s.get('device_id', ''),
            'sessionType': s.get('session_type', 'standard'),
            'ipAddress': s.get('ip_address', ''),
            'userAgent': s.get('user_agent', ''),
            'lastActive': s.get('last_active').isoformat() if s.get('last_active') else None,
            'createdAt': s.get('created_at').isoformat() if s.get('created_at') else None,
            'expiresAt': s.get('expires_at').isoformat() if s.get('expires_at') else None,
            'isCurrent': s.get('jti') == g.token_jti,
        })
    
    return success_response(data={'sessions': session_list})


@user_bp.route('/sessions/<session_id>', methods=['DELETE'])
@require_auth
@handle_errors
def revoke_session(session_id):
    """Revoke a specific session."""
    from bson import ObjectId
    from models import mongo
    
    session = mongo.db.sessions.find_one({
        '_id': ObjectId(session_id),
        'user_id': g.user_id,
        'is_revoked': False
    })
    
    if not session:
        return error_response("Session not found", 404)
    
    if session.get('jti') == g.token_jti:
        return error_response("Cannot revoke current session. Use logout instead.", 400)
    
    Session.revoke(session['jti'])
    
    return success_response(message="Session revoked successfully.")


# ---- Trusted Device Endpoints ----

@user_bp.route('/trusted-devices', methods=['GET'])
@require_auth
@handle_errors
def list_trusted_devices():
    """List all trusted devices for the current user."""
    devices = TrustedDevice.get_user_devices(g.user_id)
    
    return success_response(data={
        'devices': [TrustedDevice.to_dict(d) for d in devices]
    })


@user_bp.route('/trusted-devices/<device_id>', methods=['DELETE'])
@require_auth
@handle_errors
def revoke_trusted_device(device_id):
    """Revoke a trusted device."""
    success = TrustedDevice.revoke(g.user_id, device_id)
    
    if not success:
        return error_response("Device not found", 404)
    
    # Check if user has any remaining trusted devices
    remaining = TrustedDevice.get_user_devices(g.user_id)
    if not remaining:
        User.disable_biometric(g.user_id)
    
    AuditLog.log(
        action=AuditLog.ACTION_BIOMETRIC_DISABLE,
        user_id=g.user_id,
        details={'device_id': device_id, 'action': 'device_revoked'}
    )
    
    return success_response(message="Trusted device revoked successfully.")


@user_bp.route('/trusted-devices', methods=['DELETE'])
@require_auth
@handle_errors
def revoke_all_trusted_devices():
    """Revoke all trusted devices."""
    TrustedDevice.revoke_all(g.user_id)
    User.disable_biometric(g.user_id)
    
    AuditLog.log(
        action=AuditLog.ACTION_BIOMETRIC_DISABLE,
        user_id=g.user_id,
        details={'action': 'all_devices_revoked'}
    )
    
    return success_response(message="All trusted devices revoked.")
