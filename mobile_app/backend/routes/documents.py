"""
Document management routes for mobile app.
No S3 storage - documents stored locally on device.
Backend processes files for text extraction, embeddings, and key-value extraction.
"""

from flask import Blueprint, request, g
from bson import ObjectId
import uuid
from datetime import datetime

from models.document import Document
from models.notification import Notification
from models.audit_log import AuditLog
from services.embedding_service import EmbeddingService
from services.text_extraction_service import TextExtractionService
from services.data_extraction_service import DataExtractionService
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
    Upload a document for processing (text extraction, embeddings, key-value extraction).
    File is processed server-side but NOT stored on server (mobile keeps local copy).
    
    Form data:
        - file: The document file (PDF, JPG, PNG, WEBP)
        - type: Document type (insurance, academic, id, financial, medical, general)
        - name: (optional) Custom document name
        - hasExpiry: (optional) 'true' if document has expiry
        - expiryDate: (optional) Expiry date in ISO format
    """
    if 'file' not in request.files:
        return error_response("No file provided", 400)
    
    file = request.files['file']
    
    valid, error = Validators.validate_file(file, Config.MAX_CONTENT_LENGTH)
    if not valid:
        return error_response(error, 400)
    
    doc_type = request.form.get('type', 'general')
    name = request.form.get('name', '').strip()
    has_expiry = request.form.get('hasExpiry', '').lower() == 'true'
    expiry_date_str = request.form.get('expiryDate', '')
    
    valid, error = Validators.validate_document_type(doc_type)
    if not valid:
        return error_response(error, 400)
    
    expiry_date = None
    if has_expiry and expiry_date_str:
        try:
            expiry_date = datetime.fromisoformat(expiry_date_str.replace('Z', '+00:00'))
        except ValueError:
            return error_response("Invalid expiry date format", 400)
    
    if not name:
        name = file.filename.rsplit('.', 1)[0]
        name = Validators.sanitize_string(name, 100)
    
    # Read file content for processing
    file_content = file.read()
    file_size = len(file_content)
    mime_type = file.content_type or 'application/octet-stream'
    
    # Extract text from document (uses magic-byte detection, never trusts MIME alone)
    print(f"[Documents] Starting text extraction for '{file.filename}' ({mime_type}, {file_size} bytes)")
    extracted_text = ''
    try:
        extracted_text = TextExtractionService.extract_text(
            file_bytes=file_content,
            mime_type=mime_type,
            filename=file.filename or ''
        )
        extracted_text = TextExtractionService.clean_text(extracted_text)
        print(f"[Documents] Text extraction result: {len(extracted_text)} characters")
        if extracted_text:
            print(f"[Documents] First 200 chars: {extracted_text[:200]}")
    except Exception as e:
        print(f"[Documents] Text extraction FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    # Extract key-value data using AI
    extracted_data = {}
    if extracted_text:
        try:
            print(f"[Documents] Starting data extraction for doc type '{doc_type}'...")
            extracted_data = DataExtractionService.extract_data(extracted_text, doc_type)
            print(f"[Documents] Data extraction result: {len(extracted_data)} fields")
        except Exception as e:
            print(f"[Documents] Data extraction error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"[Documents] No text extracted, skipping data extraction")
    
    # Store document metadata in MongoDB (no S3 key)
    document = Document.create(
        user_id=g.user_id,
        name=name,
        doc_type=doc_type,
        original_filename=file.filename,
        file_size=file_size,
        mime_type=mime_type,
        has_expiry=has_expiry,
        expiry_date=expiry_date,
        extracted_text=extracted_text,
        extracted_data=extracted_data
    )
    
    # Create upload notification with push
    Notification.create(
        user_id=g.user_id,
        notification_type=Notification.TYPE_UPLOAD,
        title="Document Uploaded",
        message=f"'{name}' has been uploaded and processed successfully.",
        document_id=str(document['_id']),
        send_push=True
    )
    
    AuditLog.log(
        action=AuditLog.ACTION_DOCUMENT_UPLOAD,
        user_id=g.user_id,
        details={
            'document_id': str(document['_id']),
            'document_name': name,
            'document_type': doc_type,
            'extracted_fields': len(extracted_data),
            'text_length': len(extracted_text),
        }
    )
    
    # Generate embeddings for search/chat
    embedding_success = False
    if extracted_text:
        try:
            print(f"[Documents] Starting embedding generation...")
            chunks = EmbeddingService.chunk_text(extracted_text)
            print(f"[Documents] Created {len(chunks)} chunks")
            if chunks:
                embedding_success = EmbeddingService.store_embeddings(
                    user_id=g.user_id,
                    document_id=str(document['_id']),
                    document_name=name,
                    chunks=chunks
                )
                print(f"[Documents] Embedding storage {'succeeded' if embedding_success else 'FAILED'}")
        except Exception as e:
            print(f"[Documents] Embedding error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"[Documents] No text extracted, skipping embeddings")
    
    # Mark processing complete
    if extracted_data or embedding_success:
        Document.update(str(document['_id']), g.user_id, {'processing_status': 'completed'})
    
    return success_response(
        data={
            'document': Document.to_dict(document),
            'extractedData': extracted_data,
            'embeddingSuccess': embedding_success,
            'textLength': len(extracted_text),
            'chunksCount': len(chunks) if extracted_text and 'chunks' in dir() else 0,
        },
        message="Document uploaded and processed successfully.",
        status_code=201
    )


@documents_bp.route('/list', methods=['GET'])
@require_auth
@handle_errors
def list_documents():
    """List all documents for the current user."""
    limit = request.args.get('limit', 100, type=int)
    limit = min(limit, 500)
    
    documents = Document.find_by_user(g.user_id, limit=limit)
    
    return success_response(
        data={'documents': [Document.to_dict(doc) for doc in documents]}
    )


@documents_bp.route('/<document_id>', methods=['GET'])
@require_auth
@handle_errors
def get_document(document_id):
    """Get a single document's metadata and extracted data."""
    document = Document.find_by_id(document_id)
    
    if not document:
        return error_response("Document not found", 404)
    
    if str(document['user_id']) != g.user_id:
        return error_response("Access denied", 403)
    
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
            'extractedData': document.get('extracted_data', {}),
        }
    )


@documents_bp.route('/<document_id>/extracted-data', methods=['GET'])
@require_auth
@handle_errors
def get_extracted_data(document_id):
    """Get the extracted key-value data for a document."""
    document = Document.find_by_id(document_id)
    
    if not document:
        return error_response("Document not found", 404)
    
    if str(document['user_id']) != g.user_id:
        return error_response("Access denied", 403)
    
    return success_response(
        data={
            'documentId': document_id,
            'documentName': document.get('name'),
            'documentType': document.get('type'),
            'extractedData': document.get('extracted_data', {}),
            'processingStatus': document.get('processing_status', 'pending'),
        }
    )


@documents_bp.route('/<document_id>/re-extract', methods=['POST'])
@require_auth
@handle_errors
def re_extract_data(document_id):
    """
    Re-run AI extraction on an existing document.
    Useful if extraction was incomplete or document type changed.
    """
    document = Document.find_by_id(document_id)
    
    if not document:
        return error_response("Document not found", 404)
    
    if str(document['user_id']) != g.user_id:
        return error_response("Access denied", 403)
    
    extracted_text = document.get('extracted_text', '')
    if not extracted_text:
        return error_response("No text available for extraction. Please re-upload the document.", 400)
    
    # Allow overriding document type for better extraction
    data = request.get_json() or {}
    doc_type = data.get('type', document.get('type', 'general'))
    
    try:
        extracted_data = DataExtractionService.extract_data(extracted_text, doc_type)
    except Exception as e:
        print(f"[Documents] Re-extraction error: {e}")
        return error_response("Data extraction failed. Please try again.", 500)
    
    # Update document
    Document.update_extracted_data(document_id, extracted_data)
    Document.update(document_id, g.user_id, {'processing_status': 'completed'})
    
    return success_response(
        data={'extractedData': extracted_data},
        message="Data re-extracted successfully."
    )


@documents_bp.route('/delete/<document_id>', methods=['DELETE'])
@require_auth
@handle_errors
def delete_document(document_id):
    """Delete a document (metadata, embeddings - no S3)."""
    document = Document.find_by_id(document_id)
    
    if not document:
        return error_response("Document not found", 404)
    
    if str(document['user_id']) != g.user_id:
        return error_response("Access denied", 403)
    
    document_name = document.get('name')
    
    # Delete embeddings from Pinecone
    EmbeddingService.delete_document_embeddings(g.user_id, document_id)
    
    # Delete from MongoDB
    Document.delete(document_id, g.user_id)
    
    Notification.create(
        user_id=g.user_id,
        notification_type=Notification.TYPE_DELETE,
        title="Document Deleted",
        message=f"'{document_name}' has been deleted.",
        document_id=document_id,
        send_push=False
    )
    
    AuditLog.log(
        action=AuditLog.ACTION_DOCUMENT_DELETE,
        user_id=g.user_id,
        details={'document_id': document_id, 'document_name': document_name}
    )
    
    return success_response(message="Document deleted successfully.")


@documents_bp.route('/<document_id>', methods=['PUT', 'PATCH'])
@require_auth
@handle_errors
def update_document(document_id):
    """Update document metadata."""
    document = Document.find_by_id(document_id)
    
    if not document:
        return error_response("Document not found", 404)
    
    if str(document['user_id']) != g.user_id:
        return error_response("Access denied", 403)
    
    data = request.get_json() or {}
    update_fields = {}
    
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
    
    updated_doc = Document.find_by_id(document_id)
    
    return success_response(
        data={'document': Document.to_dict(updated_doc)},
        message="Document updated successfully."
    )


@documents_bp.route('/reindex', methods=['POST'])
@require_auth
@handle_errors
def reindex_documents():
    """Re-index all documents (regenerate embeddings)."""
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
