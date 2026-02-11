"""
Text extraction service for documents.
Handles PDF and image OCR extraction.
"""

from typing import Optional
import io


class TextExtractionService:
    """Service for extracting text from documents."""
    
    @staticmethod
    def extract_from_pdf(file_bytes: bytes) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_bytes: PDF file content as bytes
            
        Returns:
            Extracted text
        """
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            return '\n\n'.join(text_parts)
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return ""
    
    @staticmethod
    def extract_from_image(file_bytes: bytes) -> str:
        """
        Extract text from an image using OCR.
        
        Args:
            file_bytes: Image file content as bytes
            
        Returns:
            Extracted text
        """
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(io.BytesIO(file_bytes))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"OCR extraction error: {e}")
            return ""
    
    @classmethod
    def extract_text(cls, file_bytes: bytes, mime_type: str) -> str:
        """
        Extract text from a document based on its MIME type.
        
        Args:
            file_bytes: File content as bytes
            mime_type: MIME type of the file
            
        Returns:
            Extracted text
        """
        print(f"Extracting text from {mime_type} file ({len(file_bytes)} bytes)")
        
        if mime_type == 'application/pdf':
            text = cls.extract_from_pdf(file_bytes)
        elif mime_type in ['image/jpeg', 'image/png', 'image/webp']:
            text = cls.extract_from_image(file_bytes)
        else:
            text = ""
        
        print(f"Extracted {len(text)} characters of text")
        return text
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean extracted text by removing extra whitespace.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Replace multiple spaces/newlines with single
        import re
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
