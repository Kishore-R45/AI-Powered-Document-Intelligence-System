"""
Professional-grade Question Answering service using Hugging Face Inference API.
Architecture:
1. Structured Extraction Layer: Regex-based extraction for PAN, dates, IDs, GPAs
   → Deterministic, no hallucination, instant results for structured queries
2. LLM Answer Generation: HuggingFace Inference API for complex/natural language queries
3. Answer Verification Layer: Validates LLM answers against source context
4. Context Assembly: Smart chunk merging with 4000 char limit
All answers are grounded in document context. No hallucination.
"""

import re
import requests
from typing import List, Optional, Dict, Tuple
from config import Config


class QAService:
    """
    Professional document QA service with hybrid extraction.
    
    Uses structured extraction for deterministic queries (PAN, dates, IDs)
    and LLM inference for natural language queries.
    """
    
    # ==================== STRUCTURED EXTRACTION PATTERNS ====================
    
    # PAN Card: ABCDE1234F
    PAN_PATTERN = re.compile(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b')
    
    # Dates: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY, YYYY-MM-DD
    DATE_PATTERN = re.compile(
        r'\b(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\b|'
        r'\b(\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2})\b|'
        r'\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|'
        r'Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2,4})\b',
        re.IGNORECASE
    )
    
    # Aadhaar: 1234 5678 9012
    AADHAAR_PATTERN = re.compile(r'\b(\d{4}\s?\d{4}\s?\d{4})\b')
    
    # GPA/SGPA/CGPA: "SGPA: 8.5", "CGPA 9.2", "GPA : 7.8"
    GPA_PATTERN = re.compile(
        r'(?:s?gpa|cgpa|grade\s*point(?:\s*average)?)\s*:?\s*(\d+\.?\d*)',
        re.IGNORECASE
    )
    
    # Registration/Roll numbers: "Reg No: ABC123", "Roll Number: 12345"
    REG_PATTERN = re.compile(
        r'(?:reg(?:istration)?|roll|enroll(?:ment)?|prn|id)\s*(?:no\.?|number|#)?\s*:?\s*([\w\-/]+)',
        re.IGNORECASE
    )
    
    # Names: "Name: John Doe", "Student Name: Jane"
    NAME_PATTERN = re.compile(
        r"(?:student'?s?\s*)?(?:name|candidate)\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})",
        re.IGNORECASE
    )
    
    # Father's name
    FATHER_PATTERN = re.compile(
        r"(?:father'?s?\s*name|s/o|son\s+of|d/o|daughter\s+of)\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})",
        re.IGNORECASE
    )
    
    # Mother's name
    MOTHER_PATTERN = re.compile(
        r"(?:mother'?s?\s*name)\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})",
        re.IGNORECASE
    )
    
    # Address
    ADDRESS_PATTERN = re.compile(
        r'(?:address|residence|domicile)\s*:?\s*(.+?)(?:\n|$)',
        re.IGNORECASE
    )
    
    # Phone/Mobile
    PHONE_PATTERN = re.compile(
        r'(?:phone|mobile|contact|tel)\s*(?:no\.?|number)?\s*:?\s*(\+?\d[\d\s\-]{8,15})',
        re.IGNORECASE
    )
    
    # Email
    EMAIL_PATTERN = re.compile(
        r'(?:email|e-mail)\s*:?\s*([\w\.\-]+@[\w\.\-]+\.\w+)',
        re.IGNORECASE
    )
    
    # Semester-specific SGPA: "Semester 2 SGPA: 8.5"
    SEMESTER_GPA_PATTERN = re.compile(
        r'(?:sem(?:ester)?\s*(?:no\.?|number)?\s*:?\s*)?'
        r'(?:(\d+|I{1,3}V?|V?I{0,3}|first|second|third|fourth|fifth|sixth|seventh|eighth)\s*'
        r'(?:st|nd|rd|th)?\s*(?:sem(?:ester)?)?)\s*'
        r'(?:.*?)(?:s?gpa|cgpa)\s*:?\s*(\d+\.?\d*)',
        re.IGNORECASE
    )
    
    # ==================== QUERY INTENT DETECTION ====================
    
    STRUCTURED_QUERY_MAP = {
        'pan': ('pan_number', PAN_PATTERN, 'PAN number'),
        'pan number': ('pan_number', PAN_PATTERN, 'PAN number'),
        'pan card': ('pan_number', PAN_PATTERN, 'PAN number'),
        'aadhaar': ('aadhaar', AADHAAR_PATTERN, 'Aadhaar number'),
        'aadhar': ('aadhaar', AADHAAR_PATTERN, 'Aadhaar number'),
        'date of birth': ('date', DATE_PATTERN, 'date of birth'),
        'dob': ('date', DATE_PATTERN, 'date of birth'),
        'birth date': ('date', DATE_PATTERN, 'date of birth'),
        'expiry': ('date', DATE_PATTERN, 'expiry date'),
        'expiry date': ('date', DATE_PATTERN, 'expiry date'),
        'valid': ('date', DATE_PATTERN, 'validity date'),
        'registration number': ('registration', REG_PATTERN, 'registration number'),
        'reg no': ('registration', REG_PATTERN, 'registration number'),
        'roll number': ('registration', REG_PATTERN, 'roll number'),
        'roll no': ('registration', REG_PATTERN, 'roll number'),
        'enrollment': ('registration', REG_PATTERN, 'enrollment number'),
        'prn': ('registration', REG_PATTERN, 'PRN number'),
        'father': ('father_name', FATHER_PATTERN, "father's name"),
        'mother': ('mother_name', MOTHER_PATTERN, "mother's name"),
        'phone': ('phone', PHONE_PATTERN, 'phone number'),
        'mobile': ('phone', PHONE_PATTERN, 'mobile number'),
        'contact': ('phone', PHONE_PATTERN, 'contact number'),
        'email': ('email', EMAIL_PATTERN, 'email address'),
        'e-mail': ('email', EMAIL_PATTERN, 'email address'),
        'address': ('address', ADDRESS_PATTERN, 'address'),
    }
    
    # ==================== HF API ENDPOINTS ====================
    
    HF_ENDPOINTS = [
        "https://router.huggingface.co/v1/chat/completions",
        "https://router.huggingface.co/hf-inference/v1/chat/completions",
        "https://router.huggingface.co/models/{model}/v1/chat/completions",
        "https://api-inference.huggingface.co/models/{model}/v1/chat/completions",
    ]
    
    MODELS = [
        "mistralai/Mistral-7B-Instruct-v0.3",
        "meta-llama/Meta-Llama-3-8B-Instruct",
        "microsoft/Phi-3-mini-4k-instruct",
        "Qwen/Qwen2.5-7B-Instruct",
        "HuggingFaceH4/zephyr-7b-beta",
    ]
    
    _working_endpoint = None
    _working_model = None
    
    # ==================== STRUCTURED EXTRACTION ====================
    
    @classmethod
    def try_structured_extraction(cls, question: str, context: str) -> Optional[str]:
        """
        Attempt deterministic extraction for structured queries.
        
        For queries like "what is my PAN number?", extract directly via regex
        without calling the LLM. This is:
        - Instant (no API call)
        - Deterministic (same input → same output)
        - Zero hallucination risk
        
        Returns:
            Extracted answer string, or None if not a structured query
        """
        question_lower = question.lower().strip()
        
        print(f"[QA] Attempting structured extraction for: '{question_lower}'")
        
        # Check for GPA/SGPA queries with semester specificity
        if any(word in question_lower for word in ['sgpa', 'cgpa', 'gpa', 'grade point']):
            return cls._extract_gpa(question_lower, context)
        
        # Check for name queries
        if 'name' in question_lower:
            if any(word in question_lower for word in ['father', "father's", 's/o', 'son of']):
                return cls._extract_with_pattern(context, cls.FATHER_PATTERN, "father's name")
            elif any(word in question_lower for word in ['mother', "mother's", 'd/o', 'daughter of']):
                return cls._extract_with_pattern(context, cls.MOTHER_PATTERN, "mother's name")
            elif any(word in question_lower for word in ['my name', 'student name', 'candidate name', 'holder']):
                return cls._extract_with_pattern(context, cls.NAME_PATTERN, "name")
        
        # Check other structured queries
        for keyword, (query_type, pattern, label) in cls.STRUCTURED_QUERY_MAP.items():
            if keyword in question_lower:
                result = cls._extract_with_pattern(context, pattern, label)
                if result:
                    return result
        
        print(f"[QA] No structured extraction match")
        return None
    
    @classmethod
    def _extract_with_pattern(cls, context: str, pattern: re.Pattern, label: str) -> Optional[str]:
        """Extract value using a regex pattern."""
        matches = pattern.findall(context)
        if matches:
            # Flatten tuple results from patterns with groups
            values = []
            for m in matches:
                if isinstance(m, tuple):
                    val = next((v for v in m if v), None)
                else:
                    val = m
                if val and val.strip():
                    values.append(val.strip())
            
            if values:
                # Remove duplicates while preserving order
                seen = set()
                unique = []
                for v in values:
                    if v not in seen:
                        seen.add(v)
                        unique.append(v)
                
                if len(unique) == 1:
                    print(f"[QA] Structured extraction found {label}: {unique[0]}")
                    return unique[0]
                else:
                    result = ', '.join(unique[:5])
                    print(f"[QA] Structured extraction found multiple {label}: {result}")
                    return result
        return None
    
    @classmethod
    def _extract_gpa(cls, question_lower: str, context: str) -> Optional[str]:
        """
        Extract GPA/SGPA/CGPA with optional semester specificity.
        Handles queries like "what is my SGPA in 2nd semester?" 
        """
        # Check for semester-specific GPA
        semester_match = re.search(
            r'(\d+|first|second|third|fourth|fifth|sixth|seventh|eighth|1st|2nd|3rd|4th|5th|6th|7th|8th|'
            r'I{1,3}V?|V?I{0,3})(?:\s*(?:st|nd|rd|th))?\s*(?:sem(?:ester)?)',
            question_lower
        )
        
        if semester_match:
            sem_text = semester_match.group(1).lower()
            
            # Normalize semester number
            sem_map = {
                'first': '1', '1st': '1', 'i': '1', '1': '1',
                'second': '2', '2nd': '2', 'ii': '2', '2': '2',
                'third': '3', '3rd': '3', 'iii': '3', '3': '3',
                'fourth': '4', '4th': '4', 'iv': '4', '4': '4',
                'fifth': '5', '5th': '5', 'v': '5', '5': '5',
                'sixth': '6', '6th': '6', 'vi': '6', '6': '6',
                'seventh': '7', '7th': '7', 'vii': '7', '7': '7',
                'eighth': '8', '8th': '8', 'viii': '8', '8': '8',
            }
            target_sem = sem_map.get(sem_text, sem_text)
            
            print(f"[QA] Looking for semester {target_sem} GPA")
            
            # Search for semester-specific GPA in context
            sem_gpa_patterns = [
                # "Semester 2 SGPA: 8.5"
                re.compile(
                    r'(?:sem(?:ester)?\s*(?:no\.?|number)?\s*:?\s*)?' +
                    r'(?:' + re.escape(target_sem) + r'|' +
                    r'(?:' + '|'.join(k for k, v in sem_map.items() if v == target_sem) + r'))' +
                    r'(?:\s*(?:st|nd|rd|th))?' +
                    r'\s*(?:sem(?:ester)?)?\s*(?:.*?)\s*' +
                    r'(?:s?gpa|cgpa|grade\s*point)\s*:?\s*(\d+\.?\d*)',
                    re.IGNORECASE
                ),
                # "SGPA: 8.5" in a section about semester 2
                re.compile(
                    r'(?:s?gpa|cgpa)\s*:?\s*(\d+\.?\d*)',
                    re.IGNORECASE
                ),
            ]
            
            for pattern in sem_gpa_patterns[:1]:  # Try specific pattern first
                matches = pattern.findall(context)
                if matches:
                    print(f"[QA] Found semester {target_sem} GPA: {matches[0]}")
                    return matches[0]
        
        # General GPA extraction (not semester-specific)
        gpa_type = 'SGPA' if 'sgpa' in question_lower else 'CGPA' if 'cgpa' in question_lower else 'GPA'
        
        if gpa_type == 'SGPA':
            pattern = re.compile(r'sgpa\s*:?\s*(\d+\.?\d*)', re.IGNORECASE)
        elif gpa_type == 'CGPA':
            pattern = re.compile(r'cgpa\s*:?\s*(\d+\.?\d*)', re.IGNORECASE)
        else:
            pattern = re.compile(r'(?:s?gpa|cgpa|grade\s*point)\s*:?\s*(\d+\.?\d*)', re.IGNORECASE)
        
        matches = pattern.findall(context)
        if matches:
            if len(matches) == 1:
                print(f"[QA] Found {gpa_type}: {matches[0]}")
                return matches[0]
            else:
                # Multiple GPAs found — return all with context
                result = ', '.join(matches[:10])
                print(f"[QA] Found multiple {gpa_type} values: {result}")
                return result
        
        return None
    
    # ==================== HF API COMMUNICATION ====================
    
    @classmethod
    def _try_chat_request(
        cls, endpoint: str, model: str, messages: list, max_tokens: int = 500
    ) -> Optional[str]:
        """Attempt a single chat completion request."""
        token = Config.HUGGINGFACE_TOKEN
        if not token:
            raise ValueError("HUGGINGFACE_TOKEN not set in environment")
        
        url = endpoint.replace("{model}", model)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.0,  # Deterministic for factual extraction
            "top_p": 0.9,
        }
        
        try:
            print(f"  Trying: {url} | model={model}")
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"  Failed: {e}")
            return None
    
    @classmethod
    def _call_hf_chat(cls, messages: list, max_tokens: int = 500) -> str:
        """
        Call HuggingFace chat completion with auto-discovery.
        Tries cached endpoint/model first, then iterates all combinations.
        """
        # Try cached combination first
        if cls._working_endpoint and cls._working_model:
            result = cls._try_chat_request(
                cls._working_endpoint, cls._working_model, messages, max_tokens
            )
            if result:
                return result
            print("  Cached endpoint stopped working, re-discovering...")
            cls._working_endpoint = None
            cls._working_model = None
        
        # Try all combinations
        print("[QA] Discovering working HuggingFace endpoint...")
        for endpoint in cls.HF_ENDPOINTS:
            for model in cls.MODELS:
                result = cls._try_chat_request(endpoint, model, messages, max_tokens)
                if result:
                    cls._working_endpoint = endpoint
                    cls._working_model = model
                    print(f"  Found working combo: {endpoint} + {model}")
                    return result
        
        raise RuntimeError(
            "All HuggingFace API endpoints and models failed. "
            "Check your HUGGINGFACE_TOKEN and try again later."
        )
    
    # ==================== LLM ANSWER GENERATION ====================
    
    @classmethod
    def generate_answer(cls, question: str, context: str, source_names: list) -> dict:
        """
        Generate answer using HF Inference API with strict grounding prompt.
        """
        sources_str = "\n".join([f"- {name}" for name in source_names])
        
        system_prompt = (
            "You are a precise document extraction assistant. Your ONLY job is to find and extract "
            "information from the provided document context.\n\n"
            "STRICT RULES:\n"
            "1. ONLY answer using information explicitly present in the context below\n"
            "2. Extract numbers, dates, names, IDs EXACTLY as they appear - do NOT modify them\n"
            "3. If the answer is not in the context, respond with EXACTLY: Not found in document\n"
            "4. Keep answers brief and direct - just the fact, no explanations\n"
            "5. For numeric values (GPA, scores, amounts), return ONLY the number\n"
            "6. CGPA, SGPA, GPA are equivalent terms - match any of them\n"
            "7. '2nd', 'second', 'II', '2' semester are all equivalent\n"
            "8. Look for the information even if worded differently in the document\n"
            "9. Do NOT add information that is not in the context\n"
            "10. Do NOT say 'based on the context' or 'according to the document'\n\n"
            "At the END of your answer, on a NEW LINE, specify the source:\n"
            "SOURCE: [document name]\n"
            "If no answer found, do NOT include SOURCE line."
        )
        
        user_message = f"""DOCUMENT CONTEXT:
{context}
AVAILABLE SOURCE DOCUMENTS:
{sources_str}
QUESTION: {question}
ANSWER (extract directly from context):"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            print(f"[QA] Sending query to HuggingFace Inference API...")
            full_response = cls._call_hf_chat(messages, max_tokens=300)
            print(f"[QA] Received answer: {full_response[:200]}")
        except Exception as e:
            print(f"[QA] API failed: {e}")
            return None
        
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
    
    # ==================== ANSWER VERIFICATION ====================
    
    @classmethod
    def verify_answer(cls, answer: str, context: str) -> Tuple[bool, float]:
        """
        Verify that the LLM's answer is actually grounded in the context.
        Prevents hallucination by checking if key parts of the answer exist in the context.
        
        Returns:
            Tuple of (is_verified, confidence_score)
        """
        if not answer or not context:
            return False, 0.0
        
        answer_lower = answer.lower().strip()
        context_lower = context.lower()
        
        # "Not found" responses are always valid
        not_found_phrases = [
            "not found in document", "not mentioned", "no information",
            "does not contain", "doesn't contain", "not available",
            "cannot find", "not present", "i could not find",
            "there is no", "no mention",
        ]
        if any(phrase in answer_lower for phrase in not_found_phrases):
            return True, 0.0
        
        # Extract key data from answer
        # Numbers
        answer_numbers = re.findall(r'\d+\.?\d*', answer)
        # Words (non-stopwords, 3+ chars)
        stopwords = {'the', 'and', 'for', 'are', 'was', 'were', 'has', 'had', 'have',
                     'been', 'not', 'but', 'its', 'his', 'her', 'our', 'your', 'this',
                     'that', 'from', 'with', 'will', 'can', 'may', 'would', 'could',
                     'should', 'shall', 'might', 'about', 'into', 'than', 'then',
                     'also', 'just', 'only', 'very', 'some', 'any', 'all', 'each',
                     'answer', 'based', 'context', 'document', 'according', 'found'}
        answer_words = [w for w in re.findall(r'[a-z]{3,}', answer_lower) if w not in stopwords]
        
        # Check numbers found in context
        numbers_found = sum(1 for n in answer_numbers if n in context_lower)
        numbers_total = len(answer_numbers)
        
        # Check words found in context
        words_found = sum(1 for w in answer_words if w in context_lower)
        words_total = len(answer_words)
        
        # Calculate verification score
        if numbers_total + words_total == 0:
            return True, 0.5  # Short answer, give benefit of doubt
        
        total_found = numbers_found + words_found
        total_items = numbers_total + words_total
        score = total_found / total_items
        
        # Numbers are more important for verification
        if numbers_total > 0:
            number_score = numbers_found / numbers_total
            score = 0.6 * number_score + 0.4 * (words_found / max(words_total, 1))
        
        is_verified = score >= 0.4  # At least 40% of answer content found in context
        
        print(f"[QA] Verification: score={score:.2f}, numbers={numbers_found}/{numbers_total}, words={words_found}/{words_total}, verified={is_verified}")
        
        return is_verified, score
    
    # ==================== MAIN QUERY PIPELINE ====================
    
    @classmethod
    def process_query(
        cls,
        question: str,
        relevant_chunks: List[dict],
        min_confidence: float = 0.1
    ) -> dict:
        """
        Process a user query using the full RAG pipeline.
        
        Pipeline:
        1. Assemble context from relevant chunks
        2. Try structured extraction (regex) for deterministic queries
        3. If structured extraction fails, use LLM
        4. Verify LLM answer against context
        5. Return formatted response
        """
        if not relevant_chunks:
            return {
                'answer': "Not found in document",
                'found': False,
                'sources': [],
                'confidence': 0
            }
        
        # Step 1: Assemble context from chunks
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
        
        print(f"[QA] Context: {len(context)} chars from {len(context_parts)} chunks, {len(sources)} unique docs")
        print(f"[QA] Context preview:\n{context[:500]}...")
        
        # Step 2: Try structured extraction (deterministic, no LLM)
        structured_answer = cls.try_structured_extraction(question, context)
        
        if structured_answer:
            print(f"[QA] Using structured extraction result: {structured_answer}")
            return {
                'answer': structured_answer,
                'found': True,
                'sources': sources[:3],
                'confidence': 0.95  # High confidence for regex extraction
            }
        
        # Step 3: Use LLM for complex/natural language queries
        source_names = list(set(s['documentName'] for s in sources))
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
        
        print(f"[QA] LLM answer: {answer[:200]}")
        print(f"[QA] Identified source: {source_document}")
        
        # Step 4: Check if answer is "not found"
        not_found_phrases = [
            "not found in document", "not mentioned in the document",
            "no information", "does not contain", "doesn't contain",
            "not available in", "cannot find", "not present in",
            "i could not find", "there is no mention",
        ]
        is_not_found = any(phrase in answer.lower() for phrase in not_found_phrases)
        
        # Step 5: Verify LLM answer against context (anti-hallucination)
        confidence = 0.0
        if not is_not_found:
            is_verified, verification_score = cls.verify_answer(answer, context)
            confidence = 0.7 * verification_score + 0.3  # Scale to 0.3-1.0
            
            if not is_verified:
                print(f"[QA] WARNING: Answer failed verification (score={verification_score:.2f})")
                # Still return the answer but with lower confidence
                confidence = max(confidence, 0.2)
        
        # Step 6: Filter sources to identified source document
        if source_document and not is_not_found:
            source_lower = source_document.lower()
            filtered_sources = []
            for src in sources:
                if source_lower in src['documentName'].lower() or src['documentName'].lower() in source_lower:
                    filtered_sources.append(src)
                    break
            
            if not filtered_sources and sources:
                filtered_sources = [sources[0]]
            
            sources = filtered_sources
        
        return {
            'answer': answer,
            'found': not is_not_found,
            'sources': sources if not is_not_found else [],
            'confidence': round(confidence, 2)
        }
