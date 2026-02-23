"""
Dashboard routes.
Provides statistics, overview data, and recent activity.
"""

from flask import Blueprint, request, g
from datetime import datetime, timedelta

from models.document import Document
from models.notification import Notification
from models.audit_log import AuditLog
from utils.decorators import require_auth, handle_errors
from utils.responses import success_response

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@require_auth
@handle_errors
def get_stats():
    """
    Get dashboard statistics.
    
    Response:
        - totalDocuments: Total number of documents
        - documentsWithExpiry: Documents that have expiry dates
        - expiringIn1Day: Documents expiring within 1 day
        - expiringIn7Days: Documents expiring within 7 days
        - recentUploads: Last 5 uploaded documents
        - unreadNotifications: Number of unread notifications
    """
    # Get document counts
    total_documents = Document.count_by_user(g.user_id)
    documents_with_expiry = Document.count_with_expiry(g.user_id)
    
    # Get expiring documents
    expiring_1_day = len(Document.find_expiring(g.user_id, days=1))
    expiring_7_days = len(Document.find_expiring(g.user_id, days=7))
    
    # Get expired documents count
    expired = len(Document.find_expired(g.user_id))
    
    # Get recent uploads
    recent = Document.get_recent(g.user_id, limit=5)
    
    # Get unread notification count
    unread_notifications = Notification.count_unread(g.user_id)
    
    # Get recent activity from audit logs (uploads + deletes + views + queries)
    recent_activities = AuditLog.find_by_user(g.user_id, limit=30)
    activity_list = []
    for log in recent_activities:
        action = log.get('action')
        details = log.get('details', {})
        if action in ['document_upload', 'document_delete', 'document_view', 'chat_query']:
            action_type_map = {
                'document_upload': 'upload',
                'document_delete': 'delete',
                'document_view': 'view',
                'chat_query': 'query',
            }
            activity_type = action_type_map.get(action, 'view')
            
            # For chat queries, use the question as the display name
            if action == 'chat_query':
                doc_name = details.get('question', 'Document query')
                if len(doc_name) > 50:
                    doc_name = doc_name[:47] + '...'
            else:
                doc_name = details.get('document_name', 'Unknown')
            
            activity_list.append({
                'id': str(log['_id']),
                'type': activity_type,
                'documentName': doc_name,
                'timestamp': log.get('created_at').isoformat() if log.get('created_at') else None,
            })
        if len(activity_list) >= 10:
            break
    
    return success_response(data={
        'totalDocuments': total_documents,
        'documentsWithExpiry': documents_with_expiry,
        'expiringIn1Day': expiring_1_day,
        'expiringIn7Days': expiring_7_days,
        'expiredDocuments': expired,
        'recentUploads': [Document.to_dict(doc) for doc in recent],
        'recentActivity': activity_list,
        'unreadNotifications': unread_notifications
    })


@dashboard_bp.route('/expiring', methods=['GET'])
@require_auth
@handle_errors
def get_expiring_documents():
    """
    Get documents that are expiring soon.
    
    Query params:
        - days: Number of days to look ahead (default: 30)
        
    Response:
        - documents: List of expiring documents
    """
    days = request.args.get('days', 30, type=int)
    days = min(days, 365)  # Cap at 1 year
    
    documents = Document.find_expiring(g.user_id, days=days)
    
    return success_response(data={
        'documents': [Document.to_dict(doc) for doc in documents]
    })


@dashboard_bp.route('/expired', methods=['GET'])
@require_auth
@handle_errors
def get_expired_documents():
    """
    Get documents that have already expired.
    
    Response:
        - documents: List of expired documents
    """
    documents = Document.find_expired(g.user_id)
    
    return success_response(data={
        'documents': [Document.to_dict(doc) for doc in documents]
    })


@dashboard_bp.route('/timeline', methods=['GET'])
@require_auth
@handle_errors
def get_expiry_timeline():
    """
    Get expiry timeline for visualization.
    Groups documents by expiry period.
    
    Response:
        - timeline: Object with period keys and document lists
    """
    now = datetime.utcnow()
    
    # Get all documents with expiry
    all_expiring = Document.find_expiring(g.user_id, days=90)
    expired = Document.find_expired(g.user_id)
    
    # Group by period
    timeline = {
        'expired': [],
        'today': [],
        'thisWeek': [],
        'thisMonth': [],
        'later': []
    }
    
    for doc in expired:
        timeline['expired'].append(Document.to_dict(doc))
    
    for doc in all_expiring:
        expiry = doc.get('expiry_date')
        if not expiry:
            continue
        
        days_until = (expiry - now).days
        
        if days_until < 0:
            continue  # Already in expired
        elif days_until == 0:
            timeline['today'].append(Document.to_dict(doc))
        elif days_until <= 7:
            timeline['thisWeek'].append(Document.to_dict(doc))
        elif days_until <= 30:
            timeline['thisMonth'].append(Document.to_dict(doc))
        else:
            timeline['later'].append(Document.to_dict(doc))
    
    return success_response(data={'timeline': timeline})


@dashboard_bp.route('/trigger-expiry-check', methods=['POST'])
@require_auth
@handle_errors
def trigger_expiry_check():
    """
    Manually trigger the expiry reminder job.
    Useful for testing expiry notifications.
    
    Response:
        - reminders_sent: Number of reminders sent
    """
    from jobs.expiry_reminder import ExpiryReminderJob
    
    result = ExpiryReminderJob.run()
    
    return success_response(
        data={'reminders_sent': result},
        message=f"Expiry check completed. {result} reminders sent."
    )
