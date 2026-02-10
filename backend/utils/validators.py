"""
Input validation utilities.
"""

import re
from typing import Tuple, Optional
from config import Config


class Validators:
    """Input validation utilities."""
    
    # Email regex pattern
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    # Password requirements
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        email = email.strip().lower()
        
        if len(email) > 254:
            return False, "Email is too long"
        
        if not Validators.EMAIL_PATTERN.match(email):
            return False, "Invalid email format"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password strength.
        
        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < Validators.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {Validators.PASSWORD_MIN_LENGTH} characters"
        
        if len(password) > Validators.PASSWORD_MAX_LENGTH:
            return False, "Password is too long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, None
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user name.
        
        Args:
            name: Name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, "Name is required"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, "Name must be at least 2 characters"
        
        if len(name) > 100:
            return False, "Name is too long"
        
        # Allow letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            return False, "Name contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_otp(otp: str) -> Tuple[bool, Optional[str]]:
        """
        Validate OTP format.
        
        Args:
            otp: OTP to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not otp:
            return False, "Verification code is required"
        
        otp = otp.strip()
        
        if len(otp) != Config.OTP_LENGTH:
            return False, f"Verification code must be {Config.OTP_LENGTH} digits"
        
        if not otp.isdigit():
            return False, "Verification code must contain only numbers"
        
        return True, None
    
    @staticmethod
    def validate_document_type(doc_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate document type.
        
        Args:
            doc_type: Document type to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_types = ['insurance', 'academic', 'id', 'financial', 'medical', 'general']
        
        if not doc_type:
            return False, "Document type is required"
        
        if doc_type.lower() not in valid_types:
            return False, f"Invalid document type. Must be one of: {', '.join(valid_types)}"
        
        return True, None
    
    @staticmethod
    def validate_file(file, max_size: int = None) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file.
        
        Args:
            file: Flask file object
            max_size: Maximum file size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file or not file.filename:
            return False, "File is required"
        
        # Check file extension
        filename = file.filename.lower()
        allowed = Config.ALLOWED_EXTENSIONS
        
        if not any(filename.endswith(f'.{ext}') for ext in allowed):
            return False, f"File type not allowed. Allowed types: {', '.join(allowed)}"
        
        # Check file size (if seekable)
        if max_size:
            try:
                file.seek(0, 2)  # Seek to end
                size = file.tell()
                file.seek(0)  # Seek back to start
                
                if size > max_size:
                    max_mb = max_size / (1024 * 1024)
                    return False, f"File size exceeds {max_mb:.1f}MB limit"
            except Exception:
                pass  # Can't check size, continue
        
        return True, None
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """
        Sanitize a string input.
        
        Args:
            value: String to sanitize
            max_length: Maximum length
            
        Returns:
            Sanitized string
        """
        if not value:
            return ""
        
        # Strip whitespace
        value = value.strip()
        
        # Truncate if too long
        if len(value) > max_length:
            value = value[:max_length]
        
        return value
