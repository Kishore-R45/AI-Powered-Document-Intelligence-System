"""
Document management routes.
Handles document upload, listing, viewing, and deletion.
"""

from flask import Blueprint, request, jsonify, g
from bson import ObjectId
import uuid
from datetime import datetime

from models.document import Document
from models.notification import Notification
from models.audit_log import AuditLog
from services.s3_service import S3Service
from services.embedding_service import EmbeddingService
from services.text_extraction_service import TextExtractionService
from utils.validators import Validators
from utils.decorators import require_auth, handle_errors
from utils.responses import success_response, error_response
from config import Config

documents_bp = Blueprint('documents', __name__)


@documents_bp.route('/upload', methods=['POST'])
@require_auth
@handle_errors
def upload_document():
    """
    Upload a new document.
    
    Form data:
        - file: The document file (PDF, JPG, PNG, WEBP)
        - type: Document type (insurance, academic, id, financial, medical, general)
        - name: (optional) Custom document name
        - hasExpiry: (optional) 'true' if document has expiry
        - expiryDate: (optional) Expiry date in ISO format
        
    Response:
        - document: Created document metadata
    """
    # Validate file
    if 'file' not in request.files:
        return error_response("No file provided", 400)
    
    file = request.files['file']
    
    valid, error = Validators.validate_file(file, Config.MAX_CONTENT_LENGTH)
    if not valid:
        return error_response(error, 400)
    
    # Get form data
    doc_type = request.form.get('type', 'general')
    name = request.form.get('name', '').strip()
    has_expiry = request.form.get('hasExpiry', '').lower() == 'true'
    expiry_date_str = request.form.get('expiryDate', '')
    
    # Validate document type
    valid, error = Validators.validate_document_type(doc_type)
    if not valid:
        return error_response(error, 400)
    
    # Parse expiry date
    expiry_date = None
    if has_expiry and expiry_date_str:
        try:
            expiry_date = datetime.fromisoformat(expiry_date_str.replace('Z', '+00:00'))
        except ValueError:
            return error_response("Invalid expiry date format", 400)
    
    # Use filename if no custom name provided
    if not name:
        name = file.filename.rsplit('.', 1)[0]  # Remove extension
        name = Validators.sanitize_string(name, 100)
    
    # Generate document ID
    document_id = str(uuid.uuid4())
    
    # Read file content
    file_content = file.read()
    file_size = len(file_content)
    file.seek(0)
    
    # Get MIME type
    mime_type = file.content_type or 'application/octet-stream'
    
    # Generate S3 key and upload
    s3_key = S3Service.generate_s3_key(g.user_id, document_id, file.filename)
    
    if not S3Service.upload_bytes(file_content, s3_key, mime_type):
        return error_response("Failed to upload file. Please try again.", 500)
    
    # Extract text from document
    extracted_text = TextExtractionService.extract_text(file_content, mime_type)
    extracted_text = TextExtractionService.clean_text(extracted_text)
    
    # Store document metadata in MongoDB
    document = Document.create(
        user_id=g.user_id,
        name=name,
        doc_type=doc_type,
        s3_key=s3_key,
        original_filename=file.filename,
        file_size=file_size,
        mime_type=mime_type,
        has_expiry=has_expiry,
        expiry_date=expiry_date,
        extracted_text=extracted_text
    )
    
    # Generate embeddings and store in Pinecone
    if extracted_text:
        chunks = EmbeddingService.chunk_text(extracted_text)
        if chunks:
            EmbeddingService.store_embeddings(
                user_id=g.user_id,
                document_id=str(document['_id']),
                document_name=name,
                chunks=chunks
            )
    
    # Create upload notification
    Notification.create(
        user_id=g.user_id,
        notification_type=Notification.TYPE_UPLOAD,
        title="Document Uploaded",
        message=f"'{name}' has been uploaded successfully.",
        document_id=str(document['_id'])
    )
    
    # Log document upload
    AuditLog.log(
        action=AuditLog.ACTION_DOCUMENT_UPLOAD,
        user_id=g.user_id,
        details={
            'document_id': str(document['_id']),
            'document_name': name,
            'document_type': doc_type
        }
    )
    
    return success_response(
        data={'document': Document.to_dict(document)},
        message="Document uploaded successfully.",
        status_code=201
    )


@documents_bp.route('/list', methods=['GET'])
@require_auth
@handle_errors
def list_documents():
    """
    List all documents for the current user.
    
    Query params:
        - limit: Maximum number of documents (default: 100)
        
    Response:
        - documents: List of document metadata
    """
    limit = request.args.get('limit', 100, type=int)
    limit = min(limit, 500)  # Cap at 500
    
    documents = Document.find_by_user(g.user_id, limit=limit)
    
    return success_response(
        data={'documents': [Document.to_dict(doc) for doc in documents]}
    )


@documents_bp.route('/<document_id>', methods=['GET'])
@require_auth
@handle_errors
def get_document(document_id):
    """
    Get a single document's metadata and pre-signed URL.
    
    Response:
        - document: Document metadata
        - viewUrl: Pre-signed S3 URL for viewing
    """
    document = Document.find_by_id(document_id)
    
    if not document:
        return error_response("Document not found", 404)
    
    # Verify ownership
    if str(document['user_id']) != g.user_id:
        return error_response("Access denied", 403)
    
    # Generate pre-signed URL for viewing
    view_url = S3Service.get_presigned_url(document['s3_key'], for_download=False)
    
    if not view_url:
        return error_response("Failed to generate document URL", 500)
    
    # Log document access
    AuditLog.log(
        action=AuditLog.ACTION_DOCUMENT_VIEW,
        user_id=g.user_id,
        details={
            'document_id': document_id,
            'document_name': document.get('name')
        }
    )
    
    return success_response(
        data={
            'document': Document.to_dict(document),
            'viewUrl': view_url
        }
    )


@documents_bp.route('/view/<document_id>', methods=['GET'])
@documents_bp.route('/<document_id>/view', methods=['GET'])
@handle_errors
def view_document(document_id):
    """
    Get pre-signed URL for viewing a document.
    Supports two auth methods:
    1. Authorization header (returns JSON with url)
    2. Token query param (redirects to S3 URL for browser viewing)
    
    Query params:
        - token: JWT token for browser-based access
    """
    from flask import redirect
    from utils.jwt_utils import JWTUtils
    
    user_id = None
    is_browser_redirect = False
    
    # Try token from query param first (for browser access)
    token = request.args.get('token')
    if token:
        payload, error = JWTUtils.decode_token(token)
        if payload and not error:
            user_id = payload.get('sub')  # JWT uses 'sub' for user_id
            is_browser_redirect = True
    
    # Fall back to Authorization header
    if not user_id:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
            payload, error = JWTUtils.decode_token(token)
            if payload and not error:
                user_id = payload.get('sub')
    
    if not user_id:
        return error_response("Authorization required", 401)
    
    document = Document.find_by_id(document_id)
    
    if not document:
        return error_response("Document not found", 404)
    
    # Verify ownership
    if str(document['user_id']) != user_id:
        return error_response("Access denied", 403)
    
    # Generate pre-signed URL
    view_url = S3Service.get_presigned_url(document['s3_key'], for_download=False)
    
    if not view_url:
        return error_response("Failed to generate document URL", 500)
    
    # Log document access
    AuditLog.log(
        action=AuditLog.ACTION_DOCUMENT_VIEW,
        user_id=user_id,
        details={'document_id': document_id}
    )
    
    # Redirect for browser access, return JSON for API calls
    if is_browser_redirect:
        return redirect(view_url, code=302)
    
    return success_response(data={'url': view_url})


@documents_bp.route('/delete/<document_id>', methods=['DELETE'])
@require_auth
@handle_errors
def delete_document(document_id):
    """
    Delete a document.
    
    Response:
        - message: Success message
    """
    document = Document.find_by_id(document_id)
    
    if not document:
        return error_response("Document not found", 404)
    
    # Verify ownership
    if str(document['user_id']) != g.user_id:
        return error_response("Access denied", 403)
    
    document_name = document.get('name')
    
    # Delete from S3
    S3Service.delete_file(document['s3_key'])
    
    # Delete embeddings from Pinecone
    EmbeddingService.delete_document_embeddings(g.user_id, document_id)
    
    # Delete from MongoDB
    Document.delete(document_id, g.user_id)
    
    # Log deletion
    AuditLog.log(
        action=AuditLog.ACTION_DOCUMENT_DELETE,
        user_id=g.user_id,
        details={
            'document_id': document_id,
            'document_name': document_name
        }
    )
    
    return success_response(message="Document deleted successfully.")


@documents_bp.route('/<document_id>', methods=['PUT', 'PATCH'])
@require_auth
@handle_errors
def update_document(document_id):
    """
    Update document metadata.
    
    Request body:
        - name: (optional) New document name
        - type: (optional) New document type
        - hasExpiry: (optional) Enable/disable expiry
        - expiryDate: (optional) New expiry date
        
    Response:
        - document: Updated document metadata
    """
    document = Document.find_by_id(document_id)
    
    if not document:
        return error_response("Document not found", 404)
    
    # Verify ownership
    if str(document['user_id']) != g.user_id:
        return error_response("Access denied", 403)
    
    data = request.get_json() or {}
    update_fields = {}
    
    # Validate and apply updates
    if 'name' in data:
        name = Validators.sanitize_string(data['name'], 100)
        if name:
            update_fields['name'] = name
    
    if 'type' in data:
        valid, error = Validators.validate_document_type(data['type'])
        if valid:
            update_fields['type'] = data['type']
    
    if 'hasExpiry' in data:
        update_fields['has_expiry'] = bool(data['hasExpiry'])
    
    if 'expiryDate' in data:
        if data['expiryDate']:
            try:
                expiry_date = datetime.fromisoformat(data['expiryDate'].replace('Z', '+00:00'))
                update_fields['expiry_date'] = expiry_date
                update_fields['has_expiry'] = True
            except ValueError:
                return error_response("Invalid expiry date format", 400)
        else:
            update_fields['expiry_date'] = None
    
    if update_fields:
        Document.update(document_id, g.user_id, update_fields)
    
    # Fetch updated document
    updated_doc = Document.find_by_id(document_id)
    
    return success_response(
        data={'document': Document.to_dict(updated_doc)},
        message="Document updated successfully."
    )


@documents_bp.route('/reindex', methods=['POST'])
@require_auth
@handle_errors
def reindex_documents():
    """
    Re-index all documents for the current user.
    This regenerates embeddings for all documents in Pinecone.
    Useful when Pinecone index was recreated or embeddings were lost.
    
    Response:
        - message: Success message
        - indexed: Number of documents indexed
        - failed: Number of documents that failed
    """
    documents = Document.find_by_user(g.user_id, limit=500)
    
    indexed = 0
    failed = 0
    
    for doc in documents:
        try:
            extracted_text = doc.get('extracted_text', '')
            
            if not extracted_text:
                continue
            
            chunks = EmbeddingService.chunk_text(extracted_text)
            if chunks:
                success = EmbeddingService.store_embeddings(
                    user_id=g.user_id,
                    document_id=str(doc['_id']),
                    document_name=doc.get('name', 'Untitled'),
                    chunks=chunks
                )
                if success:
                    indexed += 1
                else:
                    failed += 1
        except Exception as e:
            print(f"Error reindexing document {doc['_id']}: {e}")
            failed += 1
    
    return success_response(
        message=f"Reindexing complete. {indexed} documents indexed, {failed} failed.",
        data={'indexed': indexed, 'failed': failed}
    )
