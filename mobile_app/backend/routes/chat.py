"""
Chat routes for mobile app.
Same as web - extractive QA against user's documents.
No S3 presigned URLs for sources (mobile has local copies).
"""

from flask import Blueprint, request, g

from config import Config
from models.document import Document
from models.chat_history import ChatHistory
from models.audit_log import AuditLog
from services.embedding_service import EmbeddingService
from services.qa_service import QAService
from utils.decorators import require_auth, handle_errors
from utils.responses import success_response, error_response

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/query', methods=['POST'])
@require_auth
@handle_errors
def query():
    """
    Process a question against user's documents using extractive QA.
    All answers are exact spans extracted from documents.
    If no answer is found, returns "Not found in document".
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    question = data.get('question', '').strip()
    
    if not question:
        return error_response("Question is required", 400)
    
    if len(question) > 1000:
        return error_response("Question is too long (max 1000 characters)", 400)
    
    # Store user message
    ChatHistory.add_message(
        user_id=g.user_id,
        role=ChatHistory.ROLE_USER,
        content=question
    )
    
    # Check if user has any documents
    doc_count = Document.count_by_user(g.user_id)
    if doc_count == 0:
        no_docs_answer = "You haven't uploaded any documents yet. Please upload documents to ask questions about them."
        ChatHistory.add_message(
            user_id=g.user_id,
            role=ChatHistory.ROLE_ASSISTANT,
            content=no_docs_answer,
            found=False
        )
        return success_response(data={
            'answer': no_docs_answer,
            'found': False,
            'sources': []
        })
    
    # ── Gather extracted key-value pair data from user's documents ──
    # This gives the QA pipeline access to structured fields (name, DOB, PAN, etc.)
    all_user_docs = Document.find_by_user(g.user_id, limit=200)
    kv_context_parts = []
    kv_source_map = {}  # doc_id -> {documentName, documentType}
    for doc in all_user_docs:
        extracted_data = doc.get('extracted_data', {})
        if extracted_data:
            doc_id = str(doc['_id'])
            doc_name = doc.get('name', 'Unknown')
            doc_type = doc.get('type', 'general')
            kv_source_map[doc_id] = {
                'documentId': doc_id,
                'documentName': doc_name,
                'documentType': doc_type,
            }
            lines = [f"[Document: {doc_name}]"]
            for key, value in extracted_data.items():
                lines.append(f"  {key}: {value}")
            kv_context_parts.append("\n".join(lines))
    
    kv_context = "\n\n".join(kv_context_parts) if kv_context_parts else ""
    if kv_context:
        print(f"[Chat] Assembled {len(kv_context)} chars of extracted KV data from {len(kv_context_parts)} documents")
    
    # Search for relevant chunks using hybrid retrieval (semantic + keyword boost)
    print(f"Searching for relevant chunks for user {g.user_id}")
    relevant_chunks = EmbeddingService.search_similar(
        user_id=g.user_id,
        query=question,
        top_k=Config.RAG_TOP_K,
        score_threshold=Config.RAG_SCORE_THRESHOLD
    )
    print(f"Found {len(relevant_chunks)} relevant chunks")
    
    if not relevant_chunks and not kv_context:
        not_found_answer = "Not found in document"
        ChatHistory.add_message(
            user_id=g.user_id,
            role=ChatHistory.ROLE_ASSISTANT,
            content=not_found_answer,
            found=False
        )
        AuditLog.log(
            action=AuditLog.ACTION_CHAT_QUERY,
            user_id=g.user_id,
            details={'question': question[:200], 'found': False, 'reason': 'no_relevant_chunks'}
        )
        return success_response(data={
            'answer': not_found_answer,
            'found': False,
            'sources': []
        })
    
    # Process query using extractive QA, with KV context for better accuracy
    result = QAService.process_query(
        question=question,
        relevant_chunks=relevant_chunks or [],
        min_confidence=0.1,
        kv_context=kv_context,
        kv_source_map=kv_source_map,
    )
    
    # Format sources (no presigned URLs for mobile - local files)
    sources = []
    seen_docs = set()
    
    for source in result.get('sources', []):
        doc_id = source.get('documentId')
        if doc_id and doc_id not in seen_docs:
            seen_docs.add(doc_id)
            doc = Document.find_by_id(doc_id)
            sources.append({
                'documentId': doc_id,
                'documentName': source.get('documentName', 'Unknown'),
                'documentType': doc.get('type', 'general') if doc else 'general',
            })
    
    # Fallback source from top chunk
    if not sources and result.get('found') and relevant_chunks:
        chunk = relevant_chunks[0]
        doc_id = chunk.get('document_id')
        if doc_id:
            doc = Document.find_by_id(doc_id)
            sources.append({
                'documentId': doc_id,
                'documentName': chunk.get('document_name', 'Unknown'),
                'documentType': doc.get('type', 'general') if doc else 'general',
            })
    
    answer = result.get('answer', 'Not found in document')
    found = result.get('found', False)
    
    ChatHistory.add_message(
        user_id=g.user_id,
        role=ChatHistory.ROLE_ASSISTANT,
        content=answer,
        sources=sources,
        found=found
    )
    
    AuditLog.log(
        action=AuditLog.ACTION_CHAT_QUERY,
        user_id=g.user_id,
        details={
            'question': question[:200],
            'found': found,
            'confidence': result.get('confidence', 0),
            'intent': result.get('intent')
        }
    )
    
    return success_response(data={
        'answer': answer,
        'found': found,
        'sources': sources
    })


@chat_bp.route('/history', methods=['GET'])
@require_auth
@handle_errors
def get_history():
    """Get chat history for the current user."""
    limit = request.args.get('limit', 50, type=int)
    limit = min(limit, 200)
    
    messages = ChatHistory.get_history(g.user_id, limit=limit)
    messages.reverse()  # Oldest first
    
    return success_response(data={
        'messages': [ChatHistory.to_dict(msg) for msg in messages]
    })


@chat_bp.route('/history', methods=['DELETE'])
@require_auth
@handle_errors
def clear_history():
    """Clear chat history for the current user."""
    deleted_count = ChatHistory.clear_history(g.user_id)
    
    return success_response(
        message=f"Cleared {deleted_count} messages from chat history."
    )
