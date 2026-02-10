"""
Document model and related operations.
"""

from datetime import datetime
from bson import ObjectId
from typing import List, Optional

from models import mongo


class Document:
    """Document model for file metadata management."""
    
    collection_name = 'documents'
    
    @staticmethod
    def create(
        user_id: str,
        name: str,
        doc_type: str,
        s3_key: str,
        original_filename: str,
        file_size: int,
        mime_type: str,
        has_expiry: bool = False,
        expiry_date: datetime = None,
        extracted_text: str = None
    ) -> dict:
        """
        Create a new document metadata entry.
        
        Args:
            user_id: Owner's user ID
            name: Display name for the document
            doc_type: Document type (insurance, academic, etc.)
            s3_key: S3 storage key
            original_filename: Original uploaded filename
            file_size: File size in bytes
            mime_type: MIME type of the file
            has_expiry: Whether document has an expiry date
            expiry_date: Expiry date if applicable
            extracted_text: Text extracted from document
            
        Returns:
            Created document entry
        """
        document = {
            'user_id': ObjectId(user_id),
            'name': name,
            'type': doc_type,
            's3_key': s3_key,
            'original_filename': original_filename,
            'file_size': file_size,
            'mime_type': mime_type,
            'has_expiry': has_expiry,
            'expiry_date': expiry_date,
            'extracted_text': extracted_text,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        result = mongo.db.documents.insert_one(document)
        document['_id'] = result.inserted_id
        return document
    
    @staticmethod
    def find_by_id(document_id: str) -> dict | None:
        """Find a document by ID."""
        try:
            return mongo.db.documents.find_one({'_id': ObjectId(document_id)})
        except Exception:
            return None
    
    @staticmethod
    def find_by_user(user_id: str, limit: int = 100) -> List[dict]:
        """Find all documents for a user."""
        return list(mongo.db.documents.find(
            {'user_id': ObjectId(user_id)}
        ).sort('created_at', -1).limit(limit))
    
    @staticmethod
    def find_expiring(user_id: str = None, days: int = 7) -> List[dict]:
        """Find documents expiring within specified days."""
        from datetime import timedelta
        
        now = datetime.utcnow()
        expiry_threshold = now + timedelta(days=days)
        
        query = {
            'has_expiry': True,
            'expiry_date': {
                '$gte': now,
                '$lte': expiry_threshold
            }
        }
        
        if user_id:
            query['user_id'] = ObjectId(user_id)
        
        return list(mongo.db.documents.find(query).sort('expiry_date', 1))
    
    @staticmethod
    def find_expired(user_id: str = None) -> List[dict]:
        """Find documents that have already expired."""
        now = datetime.utcnow()
        
        query = {
            'has_expiry': True,
            'expiry_date': {'$lt': now}
        }
        
        if user_id:
            query['user_id'] = ObjectId(user_id)
        
        return list(mongo.db.documents.find(query).sort('expiry_date', 1))
    
    @staticmethod
    def count_by_user(user_id: str) -> int:
        """Count documents for a user."""
        return mongo.db.documents.count_documents({'user_id': ObjectId(user_id)})
    
    @staticmethod
    def count_with_expiry(user_id: str) -> int:
        """Count documents with expiry dates for a user."""
        return mongo.db.documents.count_documents({
            'user_id': ObjectId(user_id),
            'has_expiry': True
        })
    
    @staticmethod
    def delete(document_id: str, user_id: str) -> bool:
        """Delete a document (only if user owns it)."""
        result = mongo.db.documents.delete_one({
            '_id': ObjectId(document_id),
            'user_id': ObjectId(user_id)
        })
        return result.deleted_count > 0
    
    @staticmethod
    def update(document_id: str, user_id: str, fields: dict) -> bool:
        """Update document fields."""
        fields['updated_at'] = datetime.utcnow()
        # Don't allow updating sensitive fields
        fields.pop('user_id', None)
        fields.pop('s3_key', None)
        
        result = mongo.db.documents.update_one(
            {'_id': ObjectId(document_id), 'user_id': ObjectId(user_id)},
            {'$set': fields}
        )
        return result.modified_count > 0
    
    @staticmethod
    def to_dict(doc: dict) -> dict:
        """Convert document to dictionary."""
        if not doc:
            return None
        return {
            'id': str(doc['_id']),
            'name': doc.get('name'),
            'type': doc.get('type'),
            'original_filename': doc.get('original_filename'),
            'file_size': doc.get('file_size'),
            'mime_type': doc.get('mime_type'),
            'has_expiry': doc.get('has_expiry', False),
            'expiry_date': doc.get('expiry_date').isoformat() if doc.get('expiry_date') else None,
            'created_at': doc.get('created_at').isoformat() if doc.get('created_at') else None,
            'updated_at': doc.get('updated_at').isoformat() if doc.get('updated_at') else None,
        }
    
    @staticmethod
    def get_recent(user_id: str, limit: int = 5) -> List[dict]:
        """Get recent documents for a user."""
        return list(mongo.db.documents.find(
            {'user_id': ObjectId(user_id)}
        ).sort('created_at', -1).limit(limit))
