"""
Notification routes.
Handles listing, reading, and managing notifications.
"""

from flask import Blueprint, request, g

from models.notification import Notification
from utils.decorators import require_auth, handle_errors
from utils.responses import success_response, error_response

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('', methods=['GET'])
@require_auth
@handle_errors
def list_notifications():
    """
    List notifications for the current user.
    
    Query params:
        - limit: Maximum number of notifications (default: 50)
        - unread_only: If 'true', only return unread notifications
        
    Response:
        - notifications: List of notifications
        - unreadCount: Number of unread notifications
    """
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
    """
    Mark a notification as read.
    
    Response:
        - message: Success message
    """
    success = Notification.mark_as_read(notification_id, g.user_id)
    
    if not success:
        return error_response("Notification not found or already read", 404)
    
    return success_response(message="Notification marked as read.")


@notifications_bp.route('/read-all', methods=['POST', 'PATCH'])
@require_auth
@handle_errors
def mark_all_as_read():
    """
    Mark all notifications as read.
    
    Response:
        - message: Success message
        - count: Number of notifications marked as read
    """
    count = Notification.mark_all_as_read(g.user_id)
    
    return success_response(
        message="All notifications marked as read.",
        data={'count': count}
    )


@notifications_bp.route('/<notification_id>', methods=['DELETE'])
@require_auth
@handle_errors
def delete_notification(notification_id):
    """
    Delete a notification.
    
    Response:
        - message: Success message
    """
    success = Notification.delete(notification_id, g.user_id)
    
    if not success:
        return error_response("Notification not found", 404)
    
    return success_response(message="Notification deleted.")


@notifications_bp.route('/unread-count', methods=['GET'])
@require_auth
@handle_errors
def get_unread_count():
    """
    Get count of unread notifications.
    
    Response:
        - count: Number of unread notifications
    """
    count = Notification.count_unread(g.user_id)
    
    return success_response(data={'count': count})
