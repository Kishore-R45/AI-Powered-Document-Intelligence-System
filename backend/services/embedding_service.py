"""
Professional-grade embedding service for document RAG system.
Uses sentence-transformers (all-mpnet-base-v2) for embeddings and Pinecone for vector storage.

Key features:
- Sentence-aware chunking (800 chars, 200 overlap) that preserves semantic units
- Smart preservation of numeric values, PAN numbers, dates, GPA scores
- Hybrid retrieval: semantic search + keyword boosting for structured data
- Robust metadata per chunk for precise source attribution
"""

from typing import List, Tuple
import os
import re
from config import Config


class EmbeddingService:
    """Professional embedding and retrieval service for document RAG."""
    
    _model = None
    _pinecone_index = None
    
    # --- Patterns for important structured data ---
    # PAN: ABCDE1234F
    PAN_PATTERN = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')
    # Dates: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, etc.
    DATE_PATTERN = re.compile(r'\b\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}\b|\b\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2}\b')
    # Registration / Roll numbers
    REG_PATTERN = re.compile(r'\b(?:reg(?:istration)?|roll|enroll(?:ment)?|id|prn)\s*(?:no\.?|number|#)?\s*:?\s*[\w\-/]+', re.IGNORECASE)
    # GPA / SGPA / CGPA scores
    GPA_PATTERN = re.compile(r'\b(?:s?gpa|cgpa|grade\s*point)\s*:?\s*\d+\.?\d*', re.IGNORECASE)
    # Any number with label (e.g., "Total: 450", "Marks: 89.5")
    LABELED_NUMBER_PATTERN = re.compile(r'\b[A-Za-z]+\s*:?\s*\d+\.?\d*\b')
    
    # Keywords that trigger keyword boosting in retrieval
    KEYWORD_BOOST_TRIGGERS = [
        'pan', 'register', 'registration', 'roll', 'enrollment', 'enroll',
        'id', 'number', 'prn',
        'date', 'dob', 'birth', 'expiry', 'issued', 'valid',
        'sgpa', 'cgpa', 'gpa', 'grade', 'marks', 'score', 'percentage',
        'name', 'father', 'mother', 'address', 'phone', 'mobile', 'email',
        'aadhaar', 'aadhar', 'passport', 'license', 'licence',
        'semester', 'sem', 'year', 'branch', 'department',
        'amount', 'salary', 'income', 'total', 'balance',
    ]
    
    @classmethod
    def get_model(cls):
        """Get or load the embedding model."""
        if cls._model is None:
            from sentence_transformers import SentenceTransformer
            print(f"[Embedding] Loading model: {Config.EMBEDDING_MODEL}")
            cls._model = SentenceTransformer(Config.EMBEDDING_MODEL)
            print(f"[Embedding] Model loaded. Dimension: {cls._model.get_sentence_embedding_dimension()}")
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
            
            # Get embedding dimension from model
            model = cls.get_model()
            dimension = model.get_sentence_embedding_dimension()
            
            existing_indexes = [idx.name for idx in pc.list_indexes()]
            
            if index_name not in existing_indexes:
                print(f"Creating Pinecone index '{index_name}' with dimension {dimension}...")
                pc.create_index(
                    name=index_name,
                    dimension=dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                while not pc.describe_index(index_name).status['ready']:
                    time.sleep(1)
                print(f"Pinecone index '{index_name}' created successfully.")
            else:
                # Verify existing index dimension matches
                desc = pc.describe_index(index_name)
                existing_dim = desc.dimension
                if existing_dim != dimension:
                    error_msg = (
                        f"\n{'='*70}\n"
                        f"CRITICAL ERROR: Pinecone Dimension Mismatch!\n"
                        f"{'='*70}\n"
                        f"Existing index '{index_name}' has dimension {existing_dim}\n"
                        f"But current model '{Config.EMBEDDING_MODEL}' uses dimension {dimension}\n"
                        f"\nSOLUTION:\n"
                        f"1. Go to https://app.pinecone.io/\n"
                        f"2. Delete the index '{index_name}' (or rename it for backup)\n"
                        f"3. Restart this application - it will auto-create the new index\n"
                        f"4. Re-upload all documents to re-embed with the new model\n"
                        f"\nAlternatively, change index name in .env:\n"
                        f"   PINECONE_INDEX_NAME=infovault-docs-v2\n"
                        f"{'='*70}\n"
                    )
                    print(error_msg)
                    raise ValueError(f"Pinecone dimension mismatch: {existing_dim} != {dimension}")
            
            cls._pinecone_index = pc.Index(index_name)
        return cls._pinecone_index
    
    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """Generate embedding for a single text."""
        model = cls.get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    @classmethod
    def generate_embeddings(cls, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        model = cls.get_model()
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings.tolist()
    
    @classmethod
    def chunk_text(cls, text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
        """
        Sentence-aware text chunking with overlap.
        
        Algorithm:
        1. Split text into sentences
        2. Group sentences into chunks up to chunk_size characters
        3. Overlap chunks by ~overlap characters (at sentence boundaries)
        4. Preserve important data (PAN, dates, IDs) — never split mid-value
        
        Args:
            text: Full document text
            chunk_size: Target max characters per chunk (default 800)
            overlap: Target overlap characters between chunks (default 200)
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        text = text.strip()
        if len(text) <= chunk_size:
            return [text]
        
        # Step 1: Split into sentences
        sentences = cls._split_into_sentences(text)
        
        if not sentences:
            return [text[:chunk_size]]
        
        # Step 2: Group sentences into chunks
        chunks = []
        current_chunk_sentences = []
        current_length = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            
            # If single sentence exceeds chunk_size, split it further
            if sentence_len > chunk_size:
                # Flush current chunk first
                if current_chunk_sentences:
                    chunks.append(' '.join(current_chunk_sentences))
                    current_chunk_sentences = []
                    current_length = 0
                
                # Force-split long sentence at word boundaries
                words = sentence.split()
                sub_chunk = ""
                for word in words:
                    if len(sub_chunk) + len(word) + 1 > chunk_size:
                        if sub_chunk:
                            chunks.append(sub_chunk.strip())
                        sub_chunk = word
                    else:
                        sub_chunk = f"{sub_chunk} {word}" if sub_chunk else word
                if sub_chunk:
                    current_chunk_sentences = [sub_chunk]
                    current_length = len(sub_chunk)
                continue
            
            # Would adding this sentence exceed chunk_size?
            if current_length + sentence_len + 1 > chunk_size and current_chunk_sentences:
                # Save current chunk
                chunks.append(' '.join(current_chunk_sentences))
                
                # Calculate overlap: carry forward last sentences totaling ~overlap chars
                overlap_sentences = []
                overlap_len = 0
                for s in reversed(current_chunk_sentences):
                    if overlap_len + len(s) + 1 <= overlap:
                        overlap_sentences.insert(0, s)
                        overlap_len += len(s) + 1
                    else:
                        break
                
                current_chunk_sentences = overlap_sentences + [sentence]
                current_length = overlap_len + sentence_len + 1
            else:
                current_chunk_sentences.append(sentence)
                current_length += sentence_len + 1
        
        # Flush remaining
        if current_chunk_sentences:
            remaining = ' '.join(current_chunk_sentences)
            # If the remaining chunk is very short, merge with last chunk
            if chunks and len(remaining) < overlap and len(chunks[-1]) + len(remaining) + 1 <= chunk_size * 1.2:
                chunks[-1] = chunks[-1] + ' ' + remaining
            else:
                chunks.append(remaining)
        
        print(f"[Chunking] Split {len(text)} chars into {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i}: {len(chunk)} chars")
        
        return chunks
    
    @staticmethod
    def _split_into_sentences(text: str) -> List[str]:
        """
        Split text into sentences using regex-based approach.
        Handles abbreviations, decimal numbers, and common edge cases.
        """
        # Normalize line breaks into spaces (preserving paragraph breaks)
        text = re.sub(r'\n\n+', ' [PARA] ', text)
        text = re.sub(r'\n', ' ', text)
        
        # Simple sentence splitting: look for sentence-ending punctuation followed by space + uppercase
        # Split at: . ! ? followed by space and capital letter, or paragraph markers
        # This is simpler and avoids complex abbreviation handling
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])|\s*\[PARA\]\s*', text)
        
        # Clean up and filter
        result = []
        for s in sentences:
            s = s.strip()
            # Skip very short fragments and filter out common false splits
            if len(s) > 10:  # Minimum sentence length
                result.append(s)
            elif len(s) > 1 and not re.match(r'^[A-Z]\.$', s):  # Not just "A." abbreviation
                result.append(s)
        
        # If no sentences found (edge case), return the whole text
        if not result and text.strip():
            result = [text.strip()]
        
        return result
    
    @classmethod
    def _extract_chunk_metadata(cls, chunk_text: str) -> dict:
        """
        Extract structured metadata from a chunk.
        Identifies PAN numbers, dates, registration numbers, GPA scores.
        """
        metadata = {}
        
        # Extract PAN numbers
        pans = cls.PAN_PATTERN.findall(chunk_text)
        if pans:
            metadata['contains_pan'] = True
            metadata['pan_values'] = ','.join(pans[:5])
        
        # Extract dates
        dates = cls.DATE_PATTERN.findall(chunk_text)
        if dates:
            metadata['contains_dates'] = True
            metadata['date_values'] = ','.join(dates[:5])
        
        # Extract GPA/SGPA mentions
        gpas = cls.GPA_PATTERN.findall(chunk_text)
        if gpas:
            metadata['contains_gpa'] = True
            metadata['gpa_values'] = ','.join(gpas[:5])
        
        # Check for registration numbers
        regs = cls.REG_PATTERN.findall(chunk_text)
        if regs:
            metadata['contains_registration'] = True
            metadata['reg_values'] = ','.join(regs[:3])
        
        return metadata
    
    @classmethod
    def store_embeddings(
        cls,
        user_id: str,
        document_id: str,
        document_name: str,
        chunks: List[str]
    ) -> bool:
        """
        Store document embeddings in Pinecone with rich metadata.
        """
        try:
            index = cls.get_pinecone_index()
            
            print(f"[Embedding] Storing embeddings for document {document_id}: {len(chunks)} chunks")
            
            embeddings = cls.generate_embeddings(chunks)
            print(f"[Embedding] Generated {len(embeddings)} embeddings (dim={len(embeddings[0]) if embeddings else 0})")
            
            vectors = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{document_id}_chunk_{i}"
                
                # Build metadata with structured data extraction
                metadata = {
                    'document_id': document_id,
                    'document_name': document_name,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'text': chunk[:1000],  # Pinecone metadata text limit
                    'full_text': chunk,
                    'chunk_length': len(chunk),
                }
                
                # Add extracted structured metadata
                chunk_meta = cls._extract_chunk_metadata(chunk)
                metadata.update(chunk_meta)
                
                vectors.append({
                    'id': vector_id,
                    'values': embedding,
                    'metadata': metadata,
                })
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                print(f"[Embedding] Upserting batch {i//batch_size + 1}: {len(batch)} vectors to namespace '{user_id}'")
                index.upsert(vectors=batch, namespace=user_id)
            
            print(f"[Embedding] Successfully stored {len(vectors)} vectors for document {document_id}")
            return True
        except Exception as e:
            print(f"[Embedding] Error storing embeddings: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @classmethod
    def search_similar(
        cls,
        user_id: str,
        query: str,
        top_k: int = 8,
        score_threshold: float = 0.3
    ) -> List[dict]:
        """
        Hybrid search: semantic similarity + keyword boosting.
        
        Strategy:
        1. Run semantic vector search (top_k results)
        2. Detect if query contains structured data keywords
        3. If yes → boost scores of chunks containing matching structured data
        4. Re-sort and return top results
        
        Args:
            user_id: User's namespace
            query: Search query
            top_k: Number of results to return (default 8 for more context)
            score_threshold: Minimum similarity score (default 0.3, lowered for better recall)
            
        Returns:
            List of matching chunks with metadata and scores
        """
        try:
            index = cls.get_pinecone_index()
            
            print(f"[Search] Query: '{query}' in namespace '{user_id}'")
            
            # Generate query embedding
            query_embedding = cls.generate_embedding(query)
            
            # Fetch more candidates for re-ranking
            fetch_k = max(top_k * 2, 15)
            
            # Search in user's namespace
            results = index.query(
                vector=query_embedding,
                top_k=fetch_k,
                namespace=user_id,
                include_metadata=True
            )
            
            raw_matches = results.get('matches', [])
            print(f"[Search] Pinecone returned {len(raw_matches)} raw matches")
            
            if not raw_matches:
                return []
            
            # Detect if query needs keyword boosting
            query_lower = query.lower()
            needs_keyword_boost = any(
                keyword in query_lower
                for keyword in cls.KEYWORD_BOOST_TRIGGERS
            )
            
            # Process and optionally boost matches
            scored_matches = []
            for match in raw_matches:
                score = match['score']
                metadata = match.get('metadata', {})
                text = metadata.get('full_text') or metadata.get('text', '')
                text_lower = text.lower()
                
                # Apply keyword boosting if query contains trigger words
                if needs_keyword_boost and text:
                    boost = cls._calculate_keyword_boost(query_lower, text_lower, metadata)
                    score = min(score + boost, 1.0)  # Cap at 1.0
                
                scored_matches.append({
                    'id': match['id'],
                    'score': score,
                    'original_score': match['score'],
                    'document_id': metadata.get('document_id'),
                    'document_name': metadata.get('document_name'),
                    'chunk_index': metadata.get('chunk_index'),
                    'total_chunks': metadata.get('total_chunks'),
                    'text': text,
                })
            
            # Sort by boosted score
            scored_matches.sort(key=lambda x: x['score'], reverse=True)
            
            # Filter by threshold and take top_k
            filtered = [m for m in scored_matches if m['score'] >= score_threshold][:top_k]
            
            for m in filtered:
                boost_note = f" (boosted from {m['original_score']:.4f})" if m['score'] != m['original_score'] else ""
                print(f"  Match: score={m['score']:.4f}{boost_note} doc={m['document_name']} chunk={m['chunk_index']}")
            
            print(f"[Search] Returning {len(filtered)} matches above threshold {score_threshold}")
            return filtered
            
        except Exception as e:
            print(f"[Search] Error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @classmethod
    def _calculate_keyword_boost(cls, query_lower: str, text_lower: str, metadata: dict) -> float:
        """
        Calculate keyword boost score for hybrid retrieval.
        Boosts chunks that contain keywords matching the query intent.
        """
        boost = 0.0
        
        # PAN query boost
        if any(word in query_lower for word in ['pan', 'pan number', 'pan card']):
            if metadata.get('contains_pan'):
                boost += 0.15
            if 'pan' in text_lower:
                boost += 0.05
        
        # Date query boost
        if any(word in query_lower for word in ['date', 'dob', 'birth', 'expiry', 'issued', 'when']):
            if metadata.get('contains_dates'):
                boost += 0.12
            if any(w in text_lower for w in ['date', 'dob', 'birth', 'born', 'expiry', 'valid', 'issued']):
                boost += 0.05
        
        # GPA/SGPA query boost
        if any(word in query_lower for word in ['sgpa', 'cgpa', 'gpa', 'grade', 'marks', 'score', 'percentage']):
            if metadata.get('contains_gpa'):
                boost += 0.15
            if any(w in text_lower for w in ['sgpa', 'cgpa', 'gpa', 'grade point', 'marks', 'score']):
                boost += 0.05
        
        # Registration/Roll number boost
        if any(word in query_lower for word in ['register', 'registration', 'roll', 'enrollment', 'id number', 'prn']):
            if metadata.get('contains_registration'):
                boost += 0.15
            if any(w in text_lower for w in ['registration', 'reg no', 'roll no', 'enrollment', 'prn']):
                boost += 0.05
        
        # Name query boost
        if any(word in query_lower for word in ['name', 'father', 'mother', 'student', 'holder']):
            if any(w in text_lower for w in ['name', 'father', 'mother', 'student', 'holder', 's/o', 'd/o', 'son of', 'daughter of']):
                boost += 0.08
        
        # Semester-specific boost
        semester_words = ['semester', 'sem', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th',
                         'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth']
        if any(word in query_lower for word in semester_words):
            if any(word in text_lower for word in semester_words):
                boost += 0.08
        
        # Generic keyword overlap boost (small)
        query_words = set(query_lower.split())
        text_words = set(text_lower.split())
        common_words = query_words.intersection(text_words)
        # Remove stopwords
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'which', 'who', 'how',
                     'my', 'your', 'in', 'of', 'on', 'at', 'to', 'for', 'from', 'with', 'and', 'or',
                     'it', 'its', 'this', 'that', 'i', 'me', 'do', 'does', 'did', 'can', 'could',
                     'will', 'would', 'shall', 'should', 'may', 'might', 'be', 'been', 'being',
                     'have', 'has', 'had', 'not', 'no', 'so', 'if', 'but', 'as'}
        meaningful_common = common_words - stopwords
        if meaningful_common:
            boost += min(len(meaningful_common) * 0.02, 0.08)
        
        return min(boost, 0.25)  # Cap total boost at 0.25
    
    @classmethod
    def delete_document_embeddings(cls, user_id: str, document_id: str) -> bool:
        """Delete all embeddings for a document."""
        try:
            index = cls.get_pinecone_index()
            index.delete(
                filter={'document_id': document_id},
                namespace=user_id
            )
            print(f"[Embedding] Deleted embeddings for document {document_id}")
            return True
        except Exception as e:
            print(f"[Embedding] Error deleting embeddings: {e}")
            return False
    
    @classmethod
    def delete_user_namespace(cls, user_id: str) -> bool:
        """Delete entire user namespace (for account deletion)."""
        try:
            index = cls.get_pinecone_index()
            index.delete(delete_all=True, namespace=user_id)
            print(f"[Embedding] Deleted namespace {user_id}")
            return True
        except Exception as e:
            print(f"[Embedding] Error deleting namespace: {e}")
            return False
