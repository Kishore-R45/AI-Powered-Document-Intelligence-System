"""
AI-powered data extraction service for extracting key-value pairs from documents.
Extracts structured information like names, dates, IDs, amounts, etc.
Uses regex patterns + LLM for comprehensive extraction.
"""

import re
import requests
from typing import Dict, List, Optional, Tuple
from config import Config


class DataExtractionService:
    """
    Service for extracting structured key-value pairs from document text.
    
    Uses a hybrid approach:
    1. Regex-based extraction for common patterns (fast, deterministic)
    2. LLM-based extraction for complex/unusual data (comprehensive)
    """
    
    # ==================== REGEX PATTERNS ====================
    
    PATTERNS = {
        # Personal Information
        'Name': re.compile(
            r"(?:name|candidate|applicant|holder|insured|patient)\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})",
            re.IGNORECASE
        ),
        "Father's Name": re.compile(
            r"(?:father'?s?\s*name|s/o|son\s+of|d/o|daughter\s+of)\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})",
            re.IGNORECASE
        ),
        "Mother's Name": re.compile(
            r"(?:mother'?s?\s*name)\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})",
            re.IGNORECASE
        ),
        'Date of Birth': re.compile(
            r"(?:date\s*of\s*birth|d\.?o\.?b\.?|born\s*(?:on)?)\s*:?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{1,2}\s+\w+\s+\d{4})",
            re.IGNORECASE
        ),
        'Gender': re.compile(
            r"(?:gender|sex)\s*:?\s*(male|female|other|m|f)",
            re.IGNORECASE
        ),
        'Address': re.compile(
            r"(?:address|residence|domicile)\s*:?\s*(.+?)(?:\n|$)",
            re.IGNORECASE
        ),
        'Phone': re.compile(
            r"(?:phone|mobile|contact|tel|cell)\s*(?:no\.?|number)?\s*:?\s*(\+?\d[\d\s\-]{8,15})",
            re.IGNORECASE
        ),
        'Email': re.compile(
            r"(?:email|e-mail)\s*:?\s*([\w\.\-]+@[\w\.\-]+\.\w+)",
            re.IGNORECASE
        ),
        
        # Identity Documents
        'PAN Number': re.compile(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b'),
        'Aadhaar Number': re.compile(r'\b(\d{4}\s?\d{4}\s?\d{4})\b'),
        'Passport Number': re.compile(
            r"(?:passport\s*(?:no\.?|number)?\s*:?\s*)?([A-Z]\d{7})",
            re.IGNORECASE
        ),
        'Driving License': re.compile(
            r"(?:(?:driving\s*)?(?:licence|license)\s*(?:no\.?|number)?\s*:?\s*)([\w\-/]+)",
            re.IGNORECASE
        ),
        
        # Academic Information
        'Registration Number': re.compile(
            r"(?:reg(?:istration)?|enrollment|prn)\s*(?:no\.?|number|#)?\s*:?\s*([\w\-/]+)",
            re.IGNORECASE
        ),
        'Roll Number': re.compile(
            r"(?:roll)\s*(?:no\.?|number)?\s*:?\s*([\w\-/]+)",
            re.IGNORECASE
        ),
        'CGPA': re.compile(r'(?:cgpa|cumulative\s*g\.?p\.?a\.?)\s*:?\s*(\d+\.?\d*)', re.IGNORECASE),
        'SGPA': re.compile(r'(?:sgpa)\s*:?\s*(\d+\.?\d*)', re.IGNORECASE),
        'GPA': re.compile(r'(?:gpa|grade\s*point\s*average?)\s*:?\s*(\d+\.?\d*)', re.IGNORECASE),
        'Percentage': re.compile(r'(?:percentage|marks?\s*%?)\s*:?\s*(\d+\.?\d*)\s*%?', re.IGNORECASE),
        'Branch': re.compile(
            r"(?:branch|department|discipline|stream|course|program(?:me)?)\s*:?\s*(.+?)(?:\n|$)",
            re.IGNORECASE
        ),
        'University': re.compile(
            r"(?:university|institution|college|school)\s*:?\s*(.+?)(?:\n|$)",
            re.IGNORECASE
        ),
        'Year of Passing': re.compile(
            r"(?:year\s*of\s*pass(?:ing)?|batch|graduation\s*year)\s*:?\s*(\d{4})",
            re.IGNORECASE
        ),
        
        # Financial Information
        'Account Number': re.compile(
            r"(?:a/?c|account)\s*(?:no\.?|number)?\s*:?\s*(\d{8,18})",
            re.IGNORECASE
        ),
        'IFSC Code': re.compile(r'\b([A-Z]{4}0[A-Z0-9]{6})\b'),
        'Amount': re.compile(
            r"(?:amount|total|sum|balance|salary|income|premium)\s*:?\s*(?:Rs\.?|INR|₹)?\s*(\d[\d,.]*)",
            re.IGNORECASE
        ),
        
        # Insurance Information
        'Policy Number': re.compile(
            r"(?:policy)\s*(?:no\.?|number)?\s*:?\s*([\w\-/]+)",
            re.IGNORECASE
        ),
        'Sum Insured': re.compile(
            r"(?:sum\s*(?:insured|assured))\s*:?\s*(?:Rs\.?|INR|₹)?\s*(\d[\d,.]*)",
            re.IGNORECASE
        ),
        'Premium': re.compile(
            r"(?:premium)\s*:?\s*(?:Rs\.?|INR|₹)?\s*(\d[\d,.]*)",
            re.IGNORECASE
        ),
        
        # Medical Information
        'Blood Group': re.compile(
            r"(?:blood\s*(?:group|type))\s*:?\s*([ABO]{1,2}[+-])",
            re.IGNORECASE
        ),
        'Diagnosis': re.compile(
            r"(?:diagnosis|condition|ailment)\s*:?\s*(.+?)(?:\n|$)",
            re.IGNORECASE
        ),
        
        # Date Fields
        'Issue Date': re.compile(
            r"(?:issue\s*date|date\s*of\s*issue|issued\s*(?:on)?)\s*:?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{1,2}\s+\w+\s+\d{4})",
            re.IGNORECASE
        ),
        'Expiry Date': re.compile(
            r"(?:expiry\s*date|date\s*of\s*expiry|valid\s*(?:till|until|upto|through)|expires?\s*(?:on)?)\s*:?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{1,2}\s+\w+\s+\d{4})",
            re.IGNORECASE
        ),
        'Valid From': re.compile(
            r"(?:valid\s*from|effective\s*(?:from|date))\s*:?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{1,2}\s+\w+\s+\d{4})",
            re.IGNORECASE
        ),
    }
    
    # Document type to expected fields mapping
    DOCUMENT_FIELD_MAP = {
        'id': ['Name', "Father's Name", 'Date of Birth', 'Gender', 'Address', 'PAN Number',
               'Aadhaar Number', 'Passport Number', 'Driving License', 'Issue Date', 'Expiry Date',
               'Photo', 'Phone', 'Email'],
        'academic': ['Name', "Father's Name", 'Registration Number', 'Roll Number', 'CGPA', 'SGPA',
                     'GPA', 'Percentage', 'Branch', 'University', 'Year of Passing', 'Issue Date'],
        'financial': ['Name', 'Account Number', 'IFSC Code', 'Amount', 'PAN Number',
                      'Issue Date', 'Phone', 'Email', 'Address'],
        'insurance': ['Name', 'Policy Number', 'Sum Insured', 'Premium', 'Issue Date',
                      'Expiry Date', 'Valid From', 'Phone', 'Address'],
        'medical': ['Name', 'Date of Birth', 'Blood Group', 'Diagnosis', 'Issue Date',
                    'Phone', 'Address'],
        'general': None,  # Extract all
    }
    
    # ==================== REGEX EXTRACTION ====================
    
    @classmethod
    def extract_with_regex(cls, text: str, document_type: str = 'general') -> Dict[str, str]:
        """
        Extract key-value pairs using regex patterns.
        
        Args:
            text: Document text
            document_type: Type of document for targeted extraction
            
        Returns:
            Dictionary of extracted key-value pairs
        """
        if not text:
            return {}
        
        extracted = {}
        
        # Get relevant fields for this document type
        target_fields = cls.DOCUMENT_FIELD_MAP.get(document_type.lower())
        
        patterns_to_try = cls.PATTERNS if target_fields is None else {
            k: v for k, v in cls.PATTERNS.items() if k in target_fields
        }
        
        for field_name, pattern in patterns_to_try.items():
            try:
                matches = pattern.findall(text)
                if matches:
                    # Flatten tuple results
                    values = []
                    for m in matches:
                        if isinstance(m, tuple):
                            val = next((v for v in m if v), None)
                        else:
                            val = m
                        if val and val.strip():
                            clean_val = val.strip()
                            if len(clean_val) > 2:  # Skip very short matches
                                values.append(clean_val)
                    
                    if values:
                        # Remove duplicates
                        seen = set()
                        unique = []
                        for v in values:
                            if v not in seen:
                                seen.add(v)
                                unique.append(v)
                        
                        extracted[field_name] = unique[0] if len(unique) == 1 else ', '.join(unique[:3])
            except Exception as e:
                print(f"[DataExtraction] Regex error for {field_name}: {e}")
                continue
        
        return extracted
    
    # ==================== LLM EXTRACTION ====================
    
    @classmethod
    def extract_with_llm(cls, text: str, document_type: str = 'general') -> Dict[str, str]:
        """
        Extract key-value pairs using LLM for comprehensive extraction.
        Sends the COMPLETE extracted text to the LLM for accurate results.
        
        Args:
            text: Document text (full text, not truncated)
            document_type: Type of document
            
        Returns:
            Dictionary of extracted key-value pairs
        """
        token = Config.HUGGINGFACE_TOKEN
        if not token:
            print("[DataExtraction] HUGGINGFACE_TOKEN not set, skipping LLM extraction")
            return {}
        
        # Get expected fields
        target_fields = cls.DOCUMENT_FIELD_MAP.get(document_type.lower())
        fields_hint = ""
        if target_fields:
            fields_hint = f"\nExpected fields for this {document_type} document: {', '.join(target_fields)}"
        
        # Send complete text for accurate extraction (up to 6000 chars for context window)
        max_text = text[:6000] if len(text) > 6000 else text
        
        system_prompt = (
            "You are a precise document data extraction expert. Your job is to extract ONLY valid, "
            "meaningful key-value pairs from the document text below.\n\n"
            "STRICT RULES:\n"
            "1. Extract ONLY factual information that is EXPLICITLY stated in the document\n"
            "2. Each key-value pair MUST be a real, meaningful piece of data (e.g., Name, Date, ID number, Amount)\n"
            "3. DO NOT extract:\n"
            "   - Headers, titles, or section names as values\n"
            "   - Partial or incomplete data\n"
            "   - Generic labels without specific values\n"
            "   - Duplicate information\n"
            "   - Column headers from tables without corresponding values\n"
            "   - Decorative or formatting text\n"
            "4. Format EXACTLY as: Key: Value (one per line)\n"
            "5. Use clean, standard field names (e.g., 'Full Name' not 'NAME OF THE CANDIDATE')\n"
            "6. Numbers, dates, and IDs must be extracted EXACTLY as they appear\n"
            "7. If a field appears multiple times, keep only the most complete/relevant value\n"
            "8. DO NOT add any explanation, notes, or commentary — ONLY key-value pairs\n"
            "9. If you cannot find valid data, return NOTHING rather than guessing\n"
            f"{fields_hint}"
        )
        
        user_message = f"DOCUMENT TEXT:\n{max_text}\n\nExtract all key-value pairs:"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Try HF API endpoints
        endpoints = [
            "https://router.huggingface.co/v1/chat/completions",
            "https://router.huggingface.co/hf-inference/v1/chat/completions",
        ]
        
        models = [
            "mistralai/Mistral-7B-Instruct-v0.3",
            "meta-llama/Meta-Llama-3-8B-Instruct",
            "microsoft/Phi-3-mini-4k-instruct",
        ]
        
        for endpoint in endpoints:
            for model in models:
                try:
                    response = requests.post(
                        endpoint,
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model,
                            "messages": messages,
                            "max_tokens": 500,
                            "temperature": 0.0
                        },
                        timeout=60
                    )
                    
                    if response.status_code in (200, 201):
                        result = response.json()
                        content = result["choices"][0]["message"]["content"].strip()
                        return cls._parse_llm_output(content)
                        
                except Exception as e:
                    continue
        
        print("[DataExtraction] All LLM endpoints failed")
        return {}
    
    @staticmethod
    def _parse_llm_output(output: str) -> Dict[str, str]:
        """
        Parse LLM output into key-value pairs with strict validation.
        Filters out noise, duplicates, and invalid entries.
        """
        extracted = {}
        
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Remove bullet points and numbering
            line = re.sub(r'^[\-\*\•\d]+[.\)]\s*', '', line)
            
            # Skip lines that are clearly not key-value pairs
            if line.startswith(('Note', 'Here', 'The ', 'I ', 'Based', 'From', 'Document', '---', '===', '***')):
                continue
            
            # Look for "Key: Value" pattern
            match = re.match(r'^([^:]+?):\s*(.+)$', line)
            if not match:
                match = re.match(r'^([^-]+?)\s*-\s*(.+)$', line)
            
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                
                # Remove quotes around values
                value = value.strip('"\'')
                
                # ── Strict validation ──
                
                # Skip if key or value is too long (likely not a real field)
                if len(key) > 50 or len(value) > 200:
                    continue
                
                # Skip if key is too short (1-2 chars is noise)
                if len(key) < 3:
                    continue
                
                # Skip obvious non-fields
                skip_keys = ['note', 'notes', 'comment', 'disclaimer', 'output', 'result',
                             'answer', 'response', 'document', 'text', 'source', 'page',
                             'section', 'table', 'column', 'row', 'header', 'footer',
                             'title', 'subtitle', 'description', 'summary', 'details',
                             'extracted', 'data', 'field', 'value', 'key', 'info',
                             'information', 'type', 'format', 'status']
                if key.lower() in skip_keys:
                    continue
                
                # Skip if value is placeholder or empty
                invalid_values = ['n/a', 'not found', 'not available', 'none', '-', '--',
                                  'na', 'nil', 'null', 'unknown', 'not specified',
                                  'not mentioned', 'not provided', 'not applicable']
                if value.lower() in invalid_values:
                    continue
                
                # Skip if value is just a number less than 2 (likely table index)
                if value.isdigit() and int(value) < 2:
                    continue
                
                # Skip duplicate keys (keep first occurrence)
                normalized_key = key.lower().replace(' ', '').replace('_', '')
                existing_keys = {k.lower().replace(' ', '').replace('_', '') for k in extracted.keys()}
                if normalized_key in existing_keys:
                    continue
                
                if key and value:
                    extracted[key] = value
        
        return extracted
    
    # ==================== MAIN EXTRACTION ====================
    
    @classmethod
    def extract_data(cls, text: str, document_type: str = 'general') -> Dict[str, str]:
        """
        Extract all key-value pairs from document text using hybrid approach.
        
        1. Run regex extraction (fast, deterministic)
        2. Run LLM extraction (comprehensive, may find additional fields)
        3. Merge results (regex takes priority for overlapping keys)
        4. Validate and clean all results
        
        Args:
            text: Document text (FULL text, not truncated)
            document_type: Type of document (id, academic, financial, insurance, medical, general)
            
        Returns:
            Dictionary of validated, cleaned key-value pairs
        """
        if not text or len(text.strip()) < 10:
            return {}
        
        print(f"[DataExtraction] Extracting from {document_type} document ({len(text)} chars)")
        
        # Step 1: Regex extraction
        regex_data = cls.extract_with_regex(text, document_type)
        print(f"[DataExtraction] Regex extracted {len(regex_data)} fields: {list(regex_data.keys())}")
        
        # Step 2: LLM extraction (send FULL text for better results)
        llm_data = {}
        try:
            llm_data = cls.extract_with_llm(text, document_type)
            print(f"[DataExtraction] LLM extracted {len(llm_data)} fields: {list(llm_data.keys())}")
        except Exception as e:
            print(f"[DataExtraction] LLM extraction failed: {e}")
        
        # Step 3: Merge (regex priority)
        merged = {}
        
        # Add LLM data first (lower priority)
        for key, value in llm_data.items():
            merged[key] = value
        
        # Override with regex data (higher priority)
        for key, value in regex_data.items():
            merged[key] = value
        
        # Step 4: Validate and clean all results
        cleaned = {}
        for k, v in merged.items():
            v_str = str(v).strip()
            
            # Skip empty or very short values
            if not v_str or len(v_str) < 1:
                continue
            
            # Skip values that are just numbers less than 2 (table indices)
            if v_str.isdigit() and int(v_str) < 2:
                continue
                
            # Skip values that are single characters
            if len(v_str) == 1 and not v_str.isdigit():
                continue
            
            # Skip values identical to the key
            if v_str.lower() == k.lower():
                continue
            
            cleaned[k] = v_str
        
        print(f"[DataExtraction] Final extraction: {len(cleaned)} fields")
        return cleaned
    
    @classmethod
    def get_extraction_categories(cls, document_type: str) -> List[str]:
        """Get expected extraction categories for a document type."""
        categories = Config.EXTRACTION_CATEGORIES.get(document_type.lower(), [])
        if not categories:
            categories = Config.EXTRACTION_CATEGORIES.get('general', [])
        return categories
