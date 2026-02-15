"""
Professional-grade text extraction service for documents.
Handles PDF (text-based AND scanned/image-based) and image OCR extraction.

Pipeline:
1. Try native PDF text extraction (PyPDF)
2. If text < 50 chars → automatically run OCR (pytesseract + pdf2image)
3. Clean extracted text (remove noise, normalize, preserve important data)
"""

from typing import Optional
import io
import re


class TextExtractionService:
    """Service for extracting text from documents with OCR fallback."""
    
    # Minimum text length to consider PDF as text-based (not scanned)
    MIN_TEXT_LENGTH = 50
    
    @staticmethod
    def extract_from_pdf(file_bytes: bytes) -> str:
        """
        Extract text from a PDF file using native text extraction.
        
        Args:
            file_bytes: PDF file content as bytes
            
        Returns:
            Extracted text
        """
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    print(f"  Warning: Could not extract text from page {page_num + 1}: {e}")
            
            return '\n\n'.join(text_parts)
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return ""
    
    @staticmethod
    def run_ocr_on_pdf(file_bytes: bytes) -> str:
        """
        Run OCR on a PDF by converting pages to images first.
        Used for scanned/image-based PDFs.
        
        Flow:
        1. Convert PDF pages to images using pdf2image
        2. Preprocess each image (grayscale + threshold)
        3. Extract text using pytesseract
        4. Combine results
        """
        try:
            from pdf2image import convert_from_bytes
            import pytesseract
            from PIL import Image, ImageFilter, ImageEnhance
            
            print("  Running OCR on PDF (scanned document detected)...")
            
            # Convert PDF pages to images
            try:
                images = convert_from_bytes(file_bytes, dpi=300)
            except Exception as e:
                print(f"  pdf2image conversion failed: {e}")
                try:
                    images = convert_from_bytes(file_bytes, dpi=200)
                except Exception as e2:
                    print(f"  pdf2image fallback also failed: {e2}")
                    return ""
            
            text_parts = []
            
            for i, image in enumerate(images):
                try:
                    processed_image = TextExtractionService._preprocess_image(image)
                    page_text = pytesseract.image_to_string(
                        processed_image,
                        config='--oem 3 --psm 6'
                    )
                    if page_text and page_text.strip():
                        text_parts.append(page_text.strip())
                        print(f"  OCR page {i + 1}: extracted {len(page_text)} chars")
                except Exception as e:
                    print(f"  OCR error on page {i + 1}: {e}")
                    continue
            
            result = '\n\n'.join(text_parts)
            print(f"  OCR total: extracted {len(result)} characters from {len(images)} pages")
            return result
            
        except ImportError as e:
            print(f"  OCR dependencies not available: {e}")
            print("  Install: pip install pdf2image pytesseract Pillow")
            return ""
        except Exception as e:
            print(f"  OCR processing error: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    @staticmethod
    def _preprocess_image(image):
        """
        Preprocess image for better OCR accuracy.
        Convert to grayscale, enhance contrast/sharpness, apply thresholding.
        """
        from PIL import Image, ImageFilter, ImageEnhance, ImageOps
        
        gray = image.convert('L')
        
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(2.0)
        
        enhancer = ImageEnhance.Sharpness(enhanced)
        sharp = enhancer.enhance(1.5)
        
        blurred = sharp.filter(ImageFilter.MedianFilter(size=3))
        
        threshold = 140
        binary = blurred.point(lambda x: 255 if x > threshold else 0, '1')
        
        return binary
    
    @staticmethod
    def extract_from_image(file_bytes: bytes) -> str:
        """
        Extract text from an image using OCR with preprocessing.
        """
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(io.BytesIO(file_bytes))
            processed = TextExtractionService._preprocess_image(image)
            text = pytesseract.image_to_string(
                processed,
                config='--oem 3 --psm 6'
            )
            return text.strip()
        except ImportError as e:
            print(f"OCR dependencies not available: {e}")
            return ""
        except Exception as e:
            print(f"OCR extraction error: {e}")
            return ""
    
    @classmethod
    def extract_text(cls, file_bytes: bytes, mime_type: str) -> str:
        """
        Extract text from a document based on its MIME type.
        For PDFs: tries native extraction first, falls back to OCR if text is too short.
        """
        print(f"[TextExtraction] Extracting text from {mime_type} file ({len(file_bytes)} bytes)")
        
        if mime_type == 'application/pdf':
            # Step 1: Try native PDF text extraction
            text = cls.extract_from_pdf(file_bytes)
            print(f"[TextExtraction] Native PDF extraction: {len(text)} characters")
            
            # Step 2: If text is too short → likely scanned PDF → run OCR
            if len(text.strip()) < cls.MIN_TEXT_LENGTH:
                print(f"[TextExtraction] Text too short ({len(text.strip())} < {cls.MIN_TEXT_LENGTH}), attempting OCR...")
                ocr_text = cls.run_ocr_on_pdf(file_bytes)
                if len(ocr_text.strip()) > len(text.strip()):
                    text = ocr_text
                    print(f"[TextExtraction] Using OCR text: {len(text)} characters")
                else:
                    print(f"[TextExtraction] OCR didn't improve, keeping native text")
            
        elif mime_type in ['image/jpeg', 'image/png', 'image/webp']:
            text = cls.extract_from_image(file_bytes)
        else:
            text = ""
        
        # Clean the extracted text
        cleaned = cls.clean_text(text)
        print(f"[TextExtraction] Final cleaned text: {len(cleaned)} characters")
        return cleaned
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Professional text cleaning pipeline.
        
        Rules:
        - Remove control characters
        - Normalize unicode
        - Remove non-ASCII noise while preserving important characters
        - Normalize whitespace
        - Preserve lines with PAN, ID numbers, dates, GPA/SGPA
        """
        if not text:
            return ""
        
        # Remove control characters (except newlines and tabs)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Normalize unicode
        try:
            import unicodedata
            text = unicodedata.normalize('NFKD', text)
        except:
            pass
        
        # Remove non-ASCII noise, keep important chars: / - : . , ( ) @ # & + = _ % ' "
        text = re.sub(r'[^\x20-\x7E\n\t]', ' ', text)
        
        # Normalize whitespace (multiple spaces → single space)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Normalize newlines (multiple blank lines → double newline)
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        # Clean up each line
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped:
                cleaned_lines.append(stripped)
            elif cleaned_lines and cleaned_lines[-1] != '':
                cleaned_lines.append('')
        
        return '\n'.join(cleaned_lines).strip()
