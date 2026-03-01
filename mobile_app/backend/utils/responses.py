"""
Response helper utilities.
"""

from flask import jsonify
from typing import Any, Optional


def success_response(data: Any = None, message: str = None, status_code: int = 200):
    """
    Create a success JSON response.
    
    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code
        
    Returns:
        Flask response tuple
    """
    response = {'success': True}
    
    if message:
        response['message'] = message
    
    if data is not None:
        if isinstance(data, dict):
            response.update(data)
        else:
            response['data'] = data
    
    return jsonify(response), status_code


def error_response(message: str, status_code: int = 400, errors: dict = None):
    """
    Create an error JSON response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        errors: Optional field-level errors
        
    Returns:
        Flask response tuple
    """
    response = {
        'success': False,
        'error': message,
        'message': message,
    }
    
    if errors:
        response['errors'] = errors
    
    return jsonify(response), status_code


def paginated_response(
    items: list,
    total: int,
    page: int = 1,
    per_page: int = 20,
    item_key: str = 'items'
):
    """
    Create a paginated JSON response.
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number
        per_page: Items per page
        item_key: Key name for items in response
        
    Returns:
        Flask response tuple
    """
    total_pages = (total + per_page - 1) // per_page
    
    return jsonify({
        'success': True,
        item_key: items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
        }
    }), 200
