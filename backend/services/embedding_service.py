"""
Embedding service for generating and managing document embeddings.
Uses sentence-transformers for embeddings and Pinecone for vector storage.
"""

from typing import List, Tuple
import os
from config import Config


class EmbeddingService:
    """Service for generating and managing document embeddings."""
    
    _model = None
    _pinecone_index = None
    
    @classmethod
    def get_model(cls):
        """Get or load the embedding model."""
        if cls._model is None:
            from sentence_transformers import SentenceTransformer
            cls._model = SentenceTransformer(Config.EMBEDDING_MODEL)
        return cls._model
    
    @classmethod
    def get_pinecone_index(cls):
        """Get or initialize Pinecone index. Creates index if it doesn't exist."""
        if cls._pinecone_index is None:
            from pinecone import Pinecone
            from pinecone import ServerlessSpec
            import time
            
            pc = Pinecone(api_key=Config.PINECONE_API_KEY)
            index_name = Config.PINECONE_INDEX_NAME
            
            # Check if index exists, create if not
            existing_indexes = [idx.name for idx in pc.list_indexes()]
            
            if index_name not in existing_indexes:
                print(f"Creating Pinecone index '{index_name}'...")
                pc.create_index(
                    name=index_name,
                    dimension=384,  # all-MiniLM-L6-v2 produces 384-dim embeddings
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                # Wait for index to be ready
                while not pc.describe_index(index_name).status['ready']:
                    time.sleep(1)
                print(f"Pinecone index '{index_name}' created successfully.")
            
            cls._pinecone_index = pc.Index(index_name)
        return cls._pinecone_index
    
    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """
        Generate embedding for a text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        model = cls.get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    @classmethod
    def generate_embeddings(cls, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        model = cls.get_model()
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    @classmethod
    def chunk_text(cls, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks for embedding.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text or len(text) <= chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence boundary
                for sep in ['. ', '.\n', '\n\n', '\n', ' ']:
                    boundary = text.rfind(sep, start + chunk_size // 2, end)
                    if boundary != -1:
                        end = boundary + len(sep)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap if end - overlap > start else end
        
        return chunks
    
    @classmethod
    def store_embeddings(
        cls,
        user_id: str,
        document_id: str,
        document_name: str,
        chunks: List[str]
    ) -> bool:
        """
        Store document embeddings in Pinecone.
        
        Args:
            user_id: User's ID (used as namespace)
            document_id: Document ID
            document_name: Document name for metadata
            chunks: Text chunks to embed and store
            
        Returns:
            True if successful
        """
        try:
            index = cls.get_pinecone_index()
            
            # Generate embeddings for all chunks
            embeddings = cls.generate_embeddings(chunks)
            
            # Prepare vectors for upsert
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{document_id}_chunk_{i}"
                vectors.append({
                    'id': vector_id,
                    'values': embedding,
                    'metadata': {
                        'document_id': document_id,
                        'document_name': document_name,
                        'chunk_index': i,
                        'text': chunk[:1000],  # Pinecone metadata limit
                        'full_text': chunk,
                    }
                })
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                index.upsert(vectors=batch, namespace=user_id)
            
            return True
        except Exception as e:
            print(f"Error storing embeddings: {e}")
            return False
    
    @classmethod
    def search_similar(
        cls,
        user_id: str,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.5
    ) -> List[dict]:
        """
        Search for similar documents/chunks.
        
        Args:
            user_id: User's namespace
            query: Search query
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            List of matching chunks with metadata and scores
        """
        try:
            index = cls.get_pinecone_index()
            
            # Generate query embedding
            query_embedding = cls.generate_embedding(query)
            
            # Search in user's namespace
            results = index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=user_id,
                include_metadata=True
            )
            
            # Filter by score threshold and format results
            matches = []
            for match in results.get('matches', []):
                if match['score'] >= score_threshold:
                    matches.append({
                        'id': match['id'],
                        'score': match['score'],
                        'document_id': match['metadata'].get('document_id'),
                        'document_name': match['metadata'].get('document_name'),
                        'chunk_index': match['metadata'].get('chunk_index'),
                        'text': match['metadata'].get('full_text') or match['metadata'].get('text'),
                    })
            
            return matches
        except Exception as e:
            print(f"Error searching embeddings: {e}")
            return []
    
    @classmethod
    def delete_document_embeddings(cls, user_id: str, document_id: str) -> bool:
        """
        Delete all embeddings for a document.
        
        Args:
            user_id: User's namespace
            document_id: Document ID
            
        Returns:
            True if successful
        """
        try:
            index = cls.get_pinecone_index()
            
            # Delete by ID prefix
            index.delete(
                filter={'document_id': document_id},
                namespace=user_id
            )
            
            return True
        except Exception as e:
            print(f"Error deleting embeddings: {e}")
            return False
    
    @classmethod
    def delete_user_namespace(cls, user_id: str) -> bool:
        """
        Delete entire user namespace (for account deletion).
        
        Args:
            user_id: User's namespace
            
        Returns:
            True if successful
        """
        try:
            index = cls.get_pinecone_index()
            index.delete(delete_all=True, namespace=user_id)
            return True
        except Exception as e:
            print(f"Error deleting namespace: {e}")
            return False
