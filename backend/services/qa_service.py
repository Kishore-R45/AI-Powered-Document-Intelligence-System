"""
Question Answering service using Hugging Face Inference API.
Uses direct HTTP requests with auto-discovery of working endpoint.
No local model download - all inference runs on HF servers.
Answers are grounded in document context - no hallucination.
"""

import requests
from typing import List, Optional
from config import Config


class QAService:
    """
    Document Question Answering service using HF Inference API.
    
    Uses direct HTTP calls with automatic endpoint/model discovery.
    Tries multiple HuggingFace API endpoints and models until one works,
    then caches the working combination for subsequent calls.
    """
    
    # Multiple endpoints to try (HuggingFace has changed these)
    HF_ENDPOINTS = [
        # OpenAI-compatible format (model in body, not URL)
        "https://router.huggingface.co/v1/chat/completions",
        "https://router.huggingface.co/hf-inference/v1/chat/completions",
        # Model-in-URL format
        "https://router.huggingface.co/models/{model}/v1/chat/completions",
        "https://api-inference.huggingface.co/models/{model}/v1/chat/completions",
    ]
    
    # Multiple models to try in order of preference
    MODELS = [
        "mistralai/Mistral-7B-Instruct-v0.3",
        "meta-llama/Meta-Llama-3-8B-Instruct",
        "microsoft/Phi-3-mini-4k-instruct",
        "Qwen/Qwen2.5-7B-Instruct",
        "HuggingFaceH4/zephyr-7b-beta",
    ]
    
    # Cache working combo so we don't re-discover every call
    _working_endpoint = None
    _working_model = None
    
    @classmethod
    def _try_chat_request(
        cls, endpoint: str, model: str, messages: list, max_tokens: int = 500
    ) -> Optional[str]:
        """
        Attempt a single chat completion request.
        Returns response text on success, None on failure.
        """
        token = Config.HUGGINGFACE_TOKEN
        if not token:
            raise ValueError("HUGGINGFACE_TOKEN not set in environment")
        
        # Build URL - some endpoints have {model} placeholder, some don't
        url = endpoint.replace("{model}", model)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "top_p": 0.9,
        }
        
        try:
            print(f"  Trying: {url} | model={model}")
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            return None
    
    @classmethod
    def _call_hf_chat(cls, messages: list, max_tokens: int = 500) -> str:
        """
        Call HuggingFace chat completion with auto-discovery.
        
        Tries cached endpoint/model first. If that fails (or first call),
        iterates all endpoint+model combinations until one works.
        Caches the working combination for fast subsequent calls.
        
        Returns:
            Generated text response
            
        Raises:
            RuntimeError if all combinations fail
        """
        # 1. Try cached working combination first
        if cls._working_endpoint and cls._working_model:
            result = cls._try_chat_request(
                cls._working_endpoint, cls._working_model, messages, max_tokens
            )
            if result:
                return result
            # Cached combo broken, reset and re-discover
            print("  Cached endpoint stopped working, re-discovering...")
            cls._working_endpoint = None
            cls._working_model = None
        
        # 2. Try all endpoint + model combinations
        print("Discovering working HuggingFace endpoint...")
        for endpoint in cls.HF_ENDPOINTS:
            for model in cls.MODELS:
                result = cls._try_chat_request(endpoint, model, messages, max_tokens)
                if result:
                    # Cache the working combo
                    cls._working_endpoint = endpoint
                    cls._working_model = model
                    print(f"  ✓ Found working combo: {endpoint} + {model}")
                    return result
        
        raise RuntimeError(
            "All HuggingFace API endpoints and models failed. "
            "Check your HUGGINGFACE_TOKEN and try again later."
        )
    
    @classmethod
    def generate_answer(cls, question: str, context: str, source_names: list) -> dict:
        """
        Generate answer using HF Inference API via direct HTTP request.
        Also identifies which source document contains the answer.
        
        Args:
            question: User's question
            context: Combined document context
            source_names: List of source document names
            
        Returns:
            Dict with 'answer' and 'source_document' keys, or None on failure
        """
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
        
        try:
            print(f"Sending query to HuggingFace Inference API...")
            full_response = cls._call_hf_chat(messages)
            print(f"✓ Received answer: {full_response[:200]}")
        except Exception as e:
            print(f"✗ All API attempts failed: {e}")
            return None
        
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
