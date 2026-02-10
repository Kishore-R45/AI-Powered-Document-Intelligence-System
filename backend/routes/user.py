"""
User profile and account routes.
"""

from flask import Blueprint, request, g

from models.user import User
from models.session import Session
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
    """
    Get current user's profile.
    
    Response:
        - user: User profile data
    """
    return success_response(data={
        'user': User.to_dict(g.user)
    })


@user_bp.route('/profile', methods=['PUT', 'PATCH'])
@require_auth
@handle_errors
def update_profile():
    """
    Update current user's profile.
    
    Request body:
        - name: (optional) New name
        
    Response:
        - user: Updated user data
    """
    data = request.get_json() or {}
    update_fields = {}
    
    if 'name' in data:
        valid, error = Validators.validate_name(data['name'])
        if not valid:
            return error_response(error, 400)
        update_fields['name'] = Validators.sanitize_string(data['name'], 100)
    
    if update_fields:
        User.update(g.user_id, update_fields)
        
        # Log profile update
        AuditLog.log(
            action=AuditLog.ACTION_PROFILE_UPDATE,
            user_id=g.user_id,
            details={'updated_fields': list(update_fields.keys())}
        )
    
    # Fetch updated user
    updated_user = User.find_by_id(g.user_id)
    
    return success_response(
        data={'user': User.to_dict(updated_user)},
        message="Profile updated successfully."
    )


@user_bp.route('/change-password', methods=['POST'])
@require_auth
@handle_errors
def change_password():
    """
    Change current user's password.
    
    Request body:
        - currentPassword: Current password
        - newPassword: New password
        
    Response:
        - message: Success message
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    current_password = data.get('currentPassword', '')
    new_password = data.get('newPassword', '')
    
    if not current_password:
        return error_response("Current password is required", 400)
    
    # Validate new password
    valid, error = Validators.validate_password(new_password)
    if not valid:
        return error_response(error, 400)
    
    # Verify current password
    if not User.verify_password(g.user, current_password):
        return error_response("Current password is incorrect", 401)
    
    # Check new password is different
    if current_password == new_password:
        return error_response("New password must be different from current password", 400)
    
    # Update password
    User.update_password(g.user_id, new_password)
    
    # Revoke all other sessions (security measure)
    Session.revoke_all_for_user(g.user_id)
    
    # Log password change
    AuditLog.log(
        action=AuditLog.ACTION_PASSWORD_CHANGE,
        user_id=g.user_id
    )
    
    # Send password change notification email
    EmailService.send_password_changed(g.user['email'], g.user.get('name'))
    
    return success_response(message="Password changed successfully.")


@user_bp.route('/logout-all', methods=['POST'])
@require_auth
@handle_errors
def logout_all():
    """
    Logout from all sessions/devices.
    Revokes all JWT tokens for the user.
    
    Response:
        - message: Success message
        - count: Number of sessions terminated
    """
    count = Session.revoke_all_for_user(g.user_id)
    
    # Log session logout
    AuditLog.log(
        action=AuditLog.ACTION_SESSION_LOGOUT_ALL,
        user_id=g.user_id,
        details={'sessions_revoked': count}
    )
    
    return success_response(
        message=f"Logged out from all sessions.",
        data={'count': count}
    )
