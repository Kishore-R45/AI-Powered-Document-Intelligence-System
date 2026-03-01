"""
Notification routes for mobile app.
Includes FCM token registration/unregistration endpoints.
"""

from flask import Blueprint, request, g

from models.notification import Notification
from models.user import User
from models.audit_log import AuditLog
from services.firebase_service import FirebaseService
from utils.validators import Validators
from utils.decorators import require_auth, handle_errors
from utils.responses import success_response, error_response

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('', methods=['GET'])
@require_auth
@handle_errors
def list_notifications():
    """List notifications for the current user."""
    limit = request.args.get('limit', 50, type=int)
    limit = min(limit, 200)
    unread_only = request.args.get('unread_only', '').lower() == 'true'
    
    notifications = Notification.find_by_user(
        g.user_id,
        limit=limit,
        unread_only=unread_only
    )
    
    unread_count = Notification.count_unread(g.user_id)
    
    return success_response(data={
        'notifications': [Notification.to_dict(n) for n in notifications],
        'unreadCount': unread_count
    })


@notifications_bp.route('/<notification_id>/read', methods=['POST', 'PATCH'])
@require_auth
@handle_errors
def mark_as_read(notification_id):
    """Mark a notification as read."""
    success = Notification.mark_as_read(notification_id, g.user_id)
    
    if not success:
        return error_response("Notification not found or already read", 404)
    
    return success_response(message="Notification marked as read.")


@notifications_bp.route('/read-all', methods=['POST', 'PATCH'])
@require_auth
@handle_errors
def mark_all_as_read():
    """Mark all notifications as read."""
    count = Notification.mark_all_as_read(g.user_id)
    
    return success_response(
        message="All notifications marked as read.",
        data={'count': count}
    )


@notifications_bp.route('/<notification_id>', methods=['DELETE'])
@require_auth
@handle_errors
def delete_notification(notification_id):
    """Delete a notification."""
    success = Notification.delete(notification_id, g.user_id)
    
    if not success:
        return error_response("Notification not found", 404)
    
    return success_response(message="Notification deleted.")


@notifications_bp.route('/unread-count', methods=['GET'])
@require_auth
@handle_errors
def get_unread_count():
    """Get count of unread notifications."""
    count = Notification.count_unread(g.user_id)
    
    return success_response(data={'count': count})


@notifications_bp.route('/register-fcm', methods=['POST'])
@require_auth
@handle_errors
def register_fcm_token():
    """
    Register an FCM token for push notifications.
    Called when the mobile app initializes or token refreshes.
    """
    data = request.get_json()
    if not data:
        return error_response("Request body is required", 400)
    
    fcm_token = data.get('fcmToken', '').strip()
    
    valid, error = Validators.validate_fcm_token(fcm_token)
    if not valid:
        return error_response(error, 400)
    
    User.add_fcm_token(g.user_id, fcm_token)
    
    AuditLog.log(
        action=AuditLog.ACTION_FCM_REGISTER,
        user_id=g.user_id,
        details={'token_prefix': fcm_token[:20] + '...'}
    )
    
    return success_response(message="FCM token registered successfully.")


@notifications_bp.route('/unregister-fcm', methods=['POST'])
@require_auth
@handle_errors
def unregister_fcm_token():
    """
    Unregister an FCM token (e.g., on logout).
    """
    data = request.get_json()
    if not data:
        return error_response("Request body is required", 400)
    
    fcm_token = data.get('fcmToken', '').strip()
    
    if not fcm_token:
        return error_response("FCM token is required", 400)
    
    User.remove_fcm_token(g.user_id, fcm_token)
    
    return success_response(message="FCM token unregistered successfully.")


@notifications_bp.route('/test-push', methods=['POST'])
@require_auth
@handle_errors
def test_push_notification():
    """
    Send a test push notification to the current user.
    For debugging/testing FCM integration.
    """
    success = FirebaseService.send_to_user(
        user_id=g.user_id,
        title="Test Notification",
        body="Push notifications are working! 🎉",
        data={'type': 'test'}
    )
    
    if success:
        return success_response(message="Test push notification sent.")
    else:
        return error_response("Failed to send push notification. Check FCM token registration.", 500)
