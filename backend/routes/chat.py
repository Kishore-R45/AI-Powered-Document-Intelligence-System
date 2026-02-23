"""
Chat routes for document question answering.
CRITICAL: This endpoint uses ONLY extractive QA - NO generative AI.
"""

from flask import Blueprint, request, g

from config import Config
from models.document import Document
from models.chat_history import ChatHistory
from models.audit_log import AuditLog
from services.embedding_service import EmbeddingService
from services.qa_service import QAService
from services.s3_service import S3Service
from utils.decorators import require_auth, handle_errors
from utils.responses import success_response, error_response

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/query', methods=['POST'])
@require_auth
@handle_errors
def query():
    """
    Process a question against user's documents.
    
    IMPORTANT: This endpoint uses extractive QA only.
    It will NEVER generate, hallucinate, or invent information.
    All answers are exact spans extracted from documents.
    If no answer is found, it returns "Not found in document".
    
    Request body:
        - question: The user's question
        
    Response:
        - answer: Extracted answer or "Not found in document"
        - found: Boolean indicating if answer was found
        - sources: List of source documents
    """
    data = request.get_json()
    
    if not data:
        return error_response("Request body is required", 400)
    
    question = data.get('question', '').strip()
    
    if not question:
        return error_response("Question is required", 400)
    
    if len(question) > 1000:
        return error_response("Question is too long (max 1000 characters)", 400)
    
    # Store user message in chat history
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
    
    # Search for relevant chunks using hybrid retrieval (semantic + keyword boost)
    print(f"Searching for relevant chunks for user {g.user_id}")
    relevant_chunks = EmbeddingService.search_similar(
        user_id=g.user_id,
        query=question,
        top_k=Config.RAG_TOP_K,
        score_threshold=Config.RAG_SCORE_THRESHOLD
    )
    print(f"Found {len(relevant_chunks)} relevant chunks")
    
    if not relevant_chunks:
        not_found_answer = "Not found in document"
        
        ChatHistory.add_message(
            user_id=g.user_id,
            role=ChatHistory.ROLE_ASSISTANT,
            content=not_found_answer,
            found=False
        )
        
        # Log query
        AuditLog.log(
            action=AuditLog.ACTION_CHAT_QUERY,
            user_id=g.user_id,
            details={
                'question': question[:200],
                'found': False,
                'reason': 'no_relevant_chunks'
            }
        )
        
        return success_response(data={
            'answer': not_found_answer,
            'found': False,
            'sources': []
        })
    
    # Process query using extractive QA
    result = QAService.process_query(
        question=question,
        relevant_chunks=relevant_chunks,
        min_confidence=0.1
    )
    
    # Format sources for response with presigned S3 URLs
    # process_query now returns only the single correct source document
    sources = []
    seen_docs = set()
    
    for source in result.get('sources', []):
        doc_id = source.get('documentId')
        if doc_id and doc_id not in seen_docs:
            seen_docs.add(doc_id)
            # Fetch document to get S3 key and generate presigned URL
            doc = Document.find_by_id(doc_id)
            view_url = None
            if doc and doc.get('s3_key'):
                view_url = S3Service.get_presigned_url(doc['s3_key'], for_download=False)
            sources.append({
                'documentId': doc_id,
                'documentName': source.get('documentName', 'Unknown'),
                'viewUrl': view_url
            })
    
    # Fallback: if no sources from QA but answer found, use the top relevant chunk
    if not sources and result.get('found') and relevant_chunks:
        chunk = relevant_chunks[0]
        doc_id = chunk.get('document_id')
        if doc_id:
            doc = Document.find_by_id(doc_id)
            view_url = None
            if doc and doc.get('s3_key'):
                view_url = S3Service.get_presigned_url(doc['s3_key'], for_download=False)
            sources.append({
                'documentId': doc_id,
                'documentName': chunk.get('document_name', 'Unknown'),
                'viewUrl': view_url
            })
    
    answer = result.get('answer', 'Not found in document')
    found = result.get('found', False)
    
    # Store assistant response in chat history
    ChatHistory.add_message(
        user_id=g.user_id,
        role=ChatHistory.ROLE_ASSISTANT,
        content=answer,
        sources=sources,
        found=found
    )
    
    # Log query
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
    """
    Get chat history for the current user.
    
    Query params:
        - limit: Maximum number of messages (default: 50)
        
    Response:
        - messages: List of chat messages (oldest first)
    """
    limit = request.args.get('limit', 50, type=int)
    limit = min(limit, 200)
    
    messages = ChatHistory.get_history(g.user_id, limit=limit)
    
    # Reverse to get oldest first
    messages.reverse()
    
    return success_response(data={
        'messages': [ChatHistory.to_dict(msg) for msg in messages]
    })


@chat_bp.route('/history', methods=['DELETE'])
@require_auth
@handle_errors
def clear_history():
    """
    Clear chat history for the current user.
    
    Response:
        - message: Success message
    """
    deleted_count = ChatHistory.clear_history(g.user_id)
    
    return success_response(
        message=f"Cleared {deleted_count} messages from chat history."
    )
