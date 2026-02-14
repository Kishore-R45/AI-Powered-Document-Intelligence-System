"""
Question Answering service using Hugging Face Inference API.
Uses meta-llama/Meta-Llama-3-8B-Instruct remotely via HF API.
No local model download - all inference runs on HF servers.
Answers are grounded in document context - no hallucination.
"""

from typing import List
from config import Config
from huggingface_hub import InferenceClient


class QAService:
    """
    Document Question Answering service using HF Inference API.
    
    Calls Llama 3 8B Instruct via Hugging Face's serverless Inference API.
    Uses document chunks as context with strict anti-hallucination rules.
    """
    
    _client = None
    MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
    
    @classmethod
    def get_client(cls):
        """Get or create HuggingFace InferenceClient."""
        if cls._client is None:
            token = Config.HUGGINGFACE_TOKEN
            if not token:
                raise ValueError("HUGGINGFACE_TOKEN not set in environment")
            cls._client = InferenceClient(token=token)
            print(f"✓ HuggingFace Inference API client initialized")
        return cls._client
    
    @classmethod
    def generate_answer(cls, question: str, context: str, source_names: list) -> dict:
        """
        Generate answer using HF Inference API with chat completion.
        Also identifies which source document contains the answer.
        
        Args:
            question: User's question
            context: Combined document context
            source_names: List of source document names
            
        Returns:
            Dict with 'answer' and 'source_document' keys
        """
        try:
            client = cls.get_client()
            
            # Create source list for the prompt
            sources_str = "\n".join([f"- {name}" for name in source_names])
            
            system_prompt = (
                "You are a secure document assistant. "
                "Answer ONLY using the provided context below. "
                "If the answer is not explicitly present in the context, "
                "respond with exactly: Not found in document. "
                "\n\nIMPORTANT RULES:\n"
                "- Extract numbers, dates, names exactly as they appear\n"
                "- CGPA, SGPA, GPA, and similar terms are equivalent\n"
                "- '2nd', 'second', 'II', '2' semester are equivalent\n"
                "- Look for the information even if worded differently\n"
                "- Be flexible with terminology but strict about accuracy\n"
                "- Keep answers brief and direct\n"
                "- At the end of your answer, on a NEW LINE, specify which document contains the answer using this exact format:\n"
                "  SOURCE: [document name]\n"
                "- If the answer comes from multiple documents, list only the PRIMARY source\n"
                "- If no answer found, do not include SOURCE line"
            )
            
            user_message = f"""DOCUMENT CONTEXT:
{context}

AVAILABLE SOURCE DOCUMENTS:
{sources_str}

QUESTION: {question}"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            print(f"Sending query to HF Inference API ({cls.MODEL_ID})...")
            
            response = client.chat_completion(
                messages=messages,
                model=cls.MODEL_ID,
                max_tokens=500,
                temperature=0.1,
                top_p=0.9,
            )
            
            full_response = response.choices[0].message.content.strip()
            print(f"✓ Received answer from HF API: {full_response[:200]}")
            
            # Parse answer and source from response
            answer = full_response
            source_document = None
            
            if "SOURCE:" in full_response:
                parts = full_response.rsplit("SOURCE:", 1)
                answer = parts[0].strip()
                source_document = parts[1].strip().strip("[]")
            
            return {
                'answer': answer,
                'source_document': source_document
            }
            
        except Exception as e:
            print(f"✗ HF Inference API error: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: try with a different model if Llama fails
            try:
                print("Trying fallback model: mistralai/Mistral-7B-Instruct-v0.3...")
                response = client.chat_completion(
                    messages=messages,
                    model="mistralai/Mistral-7B-Instruct-v0.3",
                    max_tokens=500,
                    temperature=0.1,
                    top_p=0.9,
                )
                full_response = response.choices[0].message.content.strip()
                print(f"✓ Fallback answer received: {full_response[:200]}")
                
                # Parse answer and source
                answer = full_response
                source_document = None
                
                if "SOURCE:" in full_response:
                    parts = full_response.rsplit("SOURCE:", 1)
                    answer = parts[0].strip()
                    source_document = parts[1].strip().strip("[]")
                
                return {
                    'answer': answer,
                    'source_document': source_document
                }
            except Exception as e2:
                print(f"✗ Fallback model also failed: {e2}")
                return None
    
    @classmethod
    def process_query(
        cls,
        question: str,
        relevant_chunks: List[dict],
        min_confidence: float = 0.1
    ) -> dict:
        """
        Process a user query using retrieved document chunks.
        
        Args:
            question: User's question
            relevant_chunks: Pre-retrieved relevant chunks from vector search
            min_confidence: Not used for LLM-based QA, kept for compatibility
            
        Returns:
            Complete response with answer, sources, and metadata
        """
        if not relevant_chunks:
            return {
                'answer': "Not found in document",
                'found': False,
                'sources': [],
                'confidence': 0
            }
        
        # Combine chunk texts into context
        context_parts = []
        sources = []
        seen_docs = set()
        total_chars = 0
        max_context_chars = 4000
        
        for chunk in relevant_chunks:
            text = chunk.get('text', '')
            if not text:
                continue
            
            if total_chars + len(text) > max_context_chars:
                break
            
            context_parts.append(text)
            total_chars += len(text)
            
            doc_id = chunk.get('document_id')
            if doc_id and doc_id not in seen_docs:
                seen_docs.add(doc_id)
                sources.append({
                    'documentId': doc_id,
                    'documentName': chunk.get('document_name', 'Unknown'),
                    'chunkIndex': chunk.get('chunk_index', 0)
                })
        
        context = "\n\n---\n\n".join(context_parts)
        
        print(f"QA context length: {len(context)} chars from {len(context_parts)} chunks")
        print(f"DEBUG - Context being sent to LLM:\n{context[:1000]}...")
        
        # Get unique source names for the LLM to identify
        source_names = list(set(s['documentName'] for s in sources))
        
        # Generate answer via HF Inference API
        result = cls.generate_answer(question, context, source_names)
        
        if not result:
            return {
                'answer': "Sorry, I couldn't process your question right now. Please try again.",
                'found': False,
                'sources': [],
                'confidence': 0
            }
        
        answer = result.get('answer', '')
        source_document = result.get('source_document')
        
        print(f"Model answer: {answer[:200]}")
        print(f"Identified source: {source_document}")
        
        # Check if model says not found
        not_found_phrases = [
            "not found in document",
            "not mentioned in the document",
            "no information",
            "does not contain",
            "doesn't contain",
            "not available in",
            "cannot find",
            "not present in"
        ]
        
        is_not_found = any(phrase in answer.lower() for phrase in not_found_phrases)
        
        # Filter sources to only the identified source document
        if source_document and not is_not_found:
            # Find matching source (case-insensitive, partial match)
            filtered_sources = []
            source_lower = source_document.lower()
            for src in sources:
                if source_lower in src['documentName'].lower() or src['documentName'].lower() in source_lower:
                    filtered_sources.append(src)
                    break  # Only one source
            
            # If no exact match, use closest match or first source
            if not filtered_sources and sources:
                filtered_sources = [sources[0]]
            
            sources = filtered_sources
        
        return {
            'answer': answer,
            'found': not is_not_found,
            'sources': sources if not is_not_found else [],
            'confidence': 0.8 if not is_not_found else 0.0
        }
