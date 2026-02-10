"""
Chat history model for storing conversation history.
"""

from datetime import datetime
from bson import ObjectId
from typing import List

from models import mongo


class ChatHistory:
    """Chat history model for storing user queries and responses."""
    
    collection_name = 'chat_history'
    
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    
    @staticmethod
    def add_message(
        user_id: str,
        role: str,
        content: str,
        sources: List[dict] = None,
        found: bool = True,
        metadata: dict = None
    ) -> dict:
        """
        Add a message to chat history.
        
        Args:
            user_id: User's ID
            role: 'user' or 'assistant'
            content: Message content
            sources: Source documents referenced (for assistant messages)
            found: Whether the answer was found in documents
            metadata: Additional metadata
            
        Returns:
            Created message entry
        """
        message = {
            'user_id': ObjectId(user_id),
            'role': role,
            'content': content,
            'sources': sources or [],
            'found': found,
            'metadata': metadata or {},
            'created_at': datetime.utcnow(),
        }
        
        result = mongo.db.chat_history.insert_one(message)
        message['_id'] = result.inserted_id
        return message
    
    @staticmethod
    def get_history(user_id: str, limit: int = 50) -> List[dict]:
        """Get chat history for a user."""
        return list(mongo.db.chat_history.find(
            {'user_id': ObjectId(user_id)}
        ).sort('created_at', -1).limit(limit))
    
    @staticmethod
    def clear_history(user_id: str) -> int:
        """Clear all chat history for a user."""
        result = mongo.db.chat_history.delete_many({'user_id': ObjectId(user_id)})
        return result.deleted_count
    
    @staticmethod
    def to_dict(message: dict) -> dict:
        """Convert message to dictionary."""
        if not message:
            return None
        return {
            'id': str(message['_id']),
            'role': message.get('role'),
            'content': message.get('content'),
            'sources': message.get('sources', []),
            'found': message.get('found', True),
            'timestamp': message.get('created_at').isoformat() if message.get('created_at') else None,
        }
