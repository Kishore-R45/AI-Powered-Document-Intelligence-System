"""
Question Answering service using extractive QA.
Uses deepset/roberta-base-squad2 for fact extraction.
Strictly NO generative answering - only exact text extraction.
"""

from typing import List, Tuple, Optional
from config import Config


class QAService:
    """
    Extractive Question Answering service.
    
    CRITICAL: This service ONLY extracts exact spans from documents.
    It NEVER generates, paraphrases, or invents information.
    """
    
    _pipeline = None
    
    @classmethod
    def get_pipeline(cls):
        """Get or load the QA pipeline."""
        if cls._pipeline is None:
            from transformers import pipeline
            cls._pipeline = pipeline(
                "question-answering",
                model=Config.QA_MODEL,
                tokenizer=Config.QA_MODEL
            )
        return cls._pipeline
    
    @classmethod
    def extract_answer(
        cls,
        question: str,
        context: str,
        min_confidence: float = 0.1
    ) -> dict:
        """
        Extract an answer from a single context.
        
        Args:
            question: The question to answer
            context: Text context to search in
            min_confidence: Minimum confidence score
            
        Returns:
            Dict with answer, score, start, end positions
        """
        try:
            qa_pipeline = cls.get_pipeline()
            
            result = qa_pipeline(
                question=question,
                context=context,
                max_answer_len=200,
                handle_impossible_answer=True
            )
            
            # Check if answer is valid
            if result['score'] < min_confidence:
                return {
                    'answer': None,
                    'score': result['score'],
                    'found': False
                }
            
            # Validate that the answer actually exists in context
            if result['answer'] not in context:
                return {
                    'answer': None,
                    'score': 0,
                    'found': False
                }
            
            return {
                'answer': result['answer'].strip(),
                'score': result['score'],
                'start': result.get('start'),
                'end': result.get('end'),
                'found': True
            }
        except Exception as e:
            print(f"QA extraction error: {e}")
            return {
                'answer': None,
                'score': 0,
                'found': False,
                'error': str(e)
            }
    
    @classmethod
    def extract_from_chunks(
        cls,
        question: str,
        chunks: List[dict],
        min_confidence: float = 0.1
    ) -> dict:
        """
        Extract the best answer from multiple chunks.
        
        Args:
            question: The question to answer
            chunks: List of chunk dicts with 'text', 'document_id', 'document_name'
            min_confidence: Minimum confidence threshold
            
        Returns:
            Best answer with source information
        """
        if not chunks:
            return {
                'answer': "Not found in document",
                'found': False,
                'sources': []
            }
        
        best_result = None
        best_score = 0
        best_chunk = None
        
        for chunk in chunks:
            text = chunk.get('text', '')
            if not text:
                continue
            
            result = cls.extract_answer(question, text, min_confidence)
            
            if result['found'] and result['score'] > best_score:
                best_score = result['score']
                best_result = result
                best_chunk = chunk
        
        if best_result and best_result['found']:
            return {
                'answer': best_result['answer'],
                'found': True,
                'confidence': best_result['score'],
                'sources': [{
                    'documentId': best_chunk.get('document_id'),
                    'documentName': best_chunk.get('document_name'),
                    'chunkIndex': best_chunk.get('chunk_index')
                }]
            }
        
        return {
            'answer': "Not found in document",
            'found': False,
            'sources': []
        }
    
    @classmethod
    def classify_query_intent(cls, question: str) -> str:
        """
        Classify the intent of a user query.
        
        Args:
            question: User's question
            
        Returns:
            Intent type: 'fact', 'explanation', 'navigation', 'unknown'
        """
        question_lower = question.lower().strip()
        
        # Fact-seeking patterns (needs extraction)
        fact_patterns = [
            'what is', 'what are', 'what was', 'what were',
            'when', 'where', 'who', 'which',
            'how many', 'how much', 'how old',
            'number', 'date', 'name', 'id', 'address',
            'policy number', 'account', 'reference',
            'expiry', 'valid', 'issue date'
        ]
        
        # Explanation patterns (may need synthesis - be careful)
        explanation_patterns = [
            'why', 'how does', 'explain', 'describe',
            'what does', 'meaning of', 'definition'
        ]
        
        # Navigation patterns
        navigation_patterns = [
            'show me', 'find', 'list', 'open',
            'where can i', 'how to'
        ]
        
        for pattern in fact_patterns:
            if pattern in question_lower:
                return 'fact'
        
        for pattern in explanation_patterns:
            if pattern in question_lower:
                return 'explanation'
        
        for pattern in navigation_patterns:
            if pattern in question_lower:
                return 'navigation'
        
        # Default to fact extraction for safety
        return 'fact'
    
    @classmethod
    def validate_answer_is_extractive(cls, answer: str, context: str) -> bool:
        """
        Validate that an answer is actually extracted from context.
        
        Args:
            answer: The proposed answer
            context: The source context
            
        Returns:
            True if answer appears in context
        """
        if not answer or not context:
            return False
        
        # Normalize for comparison
        answer_normalized = answer.lower().strip()
        context_normalized = context.lower()
        
        return answer_normalized in context_normalized
    
    @classmethod
    def process_query(
        cls,
        question: str,
        relevant_chunks: List[dict],
        min_confidence: float = 0.1
    ) -> dict:
        """
        Process a user query end-to-end.
        
        This is the main entry point for question answering.
        
        Args:
            question: User's question
            relevant_chunks: Pre-retrieved relevant chunks from vector search
            min_confidence: Minimum confidence for answers
            
        Returns:
            Complete response with answer, sources, and metadata
        """
        # Classify intent
        intent = cls.classify_query_intent(question)
        
        # Extract answer
        result = cls.extract_from_chunks(question, relevant_chunks, min_confidence)
        
        # Final validation: ensure we're not hallucinating
        if result['found'] and result.get('answer'):
            # Verify answer exists in at least one chunk
            answer_verified = False
            for chunk in relevant_chunks:
                if cls.validate_answer_is_extractive(result['answer'], chunk.get('text', '')):
                    answer_verified = True
                    break
            
            if not answer_verified:
                # Answer not found in any chunk - reject it
                result = {
                    'answer': "Not found in document",
                    'found': False,
                    'sources': []
                }
        
        return {
            'answer': result.get('answer', "Not found in document"),
            'found': result.get('found', False),
            'sources': result.get('sources', []),
            'intent': intent,
            'confidence': result.get('confidence', 0)
        }
