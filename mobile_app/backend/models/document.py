"""
Document model for mobile app.
No S3 keys - documents are stored locally on device.
Backend stores metadata + extracted text for AI processing.
"""

from datetime import datetime
from bson import ObjectId
from typing import List, Optional

from models import mongo


class Document:
    """Document model for mobile app - local storage focus."""
    
    collection_name = 'documents'
    
    @staticmethod
    def create(
        user_id: str,
        name: str,
        doc_type: str,
        original_filename: str,
        file_size: int,
        mime_type: str,
        has_expiry: bool = False,
        expiry_date: datetime = None,
        extracted_text: str = None,
        extracted_data: dict = None
    ) -> dict:
        """
        Create a new document metadata entry.
        No S3 key - documents stored locally on mobile device.
        """
        document = {
            'user_id': ObjectId(user_id),
            'name': name,
            'type': doc_type,
            'original_filename': original_filename,
            'file_size': file_size,
            'mime_type': mime_type,
            'has_expiry': has_expiry,
            'expiry_date': expiry_date,
            'extracted_text': extracted_text,
            'extracted_data': extracted_data or {},  # Key-value pairs extracted from document
            'processing_status': 'completed' if extracted_text else 'pending',
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
        fields.pop('user_id', None)
        
        result = mongo.db.documents.update_one(
            {'_id': ObjectId(document_id), 'user_id': ObjectId(user_id)},
            {'$set': fields}
        )
        return result.modified_count > 0
    
    @staticmethod
    def update_extracted_data(document_id: str, extracted_data: dict) -> bool:
        """Update extracted key-value data for a document."""
        result = mongo.db.documents.update_one(
            {'_id': ObjectId(document_id)},
            {'$set': {
                'extracted_data': extracted_data,
                'processing_status': 'completed',
                'updated_at': datetime.utcnow()
            }}
        )
        return result.modified_count > 0
    
    @staticmethod
    def get_recent(user_id: str, limit: int = 5) -> List[dict]:
        """Get recent documents for a user."""
        return list(mongo.db.documents.find(
            {'user_id': ObjectId(user_id)}
        ).sort('created_at', -1).limit(limit))
    
    @staticmethod
    def to_dict(doc: dict) -> dict:
        """Convert document to dictionary for API response."""
        if not doc:
            return None
        return {
            'id': str(doc['_id']),
            'name': doc.get('name'),
            'type': doc.get('type'),
            'originalFilename': doc.get('original_filename'),
            'fileSize': doc.get('file_size'),
            'mimeType': doc.get('mime_type'),
            'hasExpiry': doc.get('has_expiry', False),
            'expiryDate': doc.get('expiry_date').isoformat() if doc.get('expiry_date') else None,
            'extractedData': doc.get('extracted_data', {}),
            'processingStatus': doc.get('processing_status', 'completed'),
            'uploadDate': doc.get('created_at').isoformat() if doc.get('created_at') else None,
            'createdAt': doc.get('created_at').isoformat() if doc.get('created_at') else None,
            'updatedAt': doc.get('updated_at').isoformat() if doc.get('updated_at') else None,
        }
