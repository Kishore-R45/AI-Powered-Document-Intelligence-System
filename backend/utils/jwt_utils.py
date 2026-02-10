"""
JWT token utilities.
"""

import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from config import Config


class JWTUtils:
    """JWT token management utilities."""
    
    @staticmethod
    def generate_token(user_id: str, token_type: str = 'access') -> Tuple[str, str, datetime]:
        """
        Generate a JWT token.
        
        Args:
            user_id: User's ID
            token_type: 'access' or 'refresh'
            
        Returns:
            Tuple of (token, jti, expiry_datetime)
        """
        jti = str(uuid.uuid4())
        
        if token_type == 'refresh':
            expires_delta = Config.JWT_REFRESH_TOKEN_EXPIRES
        else:
            expires_delta = Config.JWT_ACCESS_TOKEN_EXPIRES
        
        expires_at = datetime.utcnow() + expires_delta
        
        payload = {
            'sub': user_id,
            'type': token_type,
            'jti': jti,
            'iat': datetime.utcnow(),
            'exp': expires_at
        }
        
        token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
        return token, jti, expires_at
    
    @staticmethod
    def decode_token(token: str) -> Tuple[Optional[dict], Optional[str]]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Tuple of (payload, error_message)
        """
        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            return payload, None
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError as e:
            return None, f"Invalid token: {str(e)}"
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[str]:
        """
        Extract user ID from a token.
        
        Args:
            token: JWT token string
            
        Returns:
            User ID or None if invalid
        """
        payload, error = JWTUtils.decode_token(token)
        if payload:
            return payload.get('sub')
        return None
    
    @staticmethod
    def get_token_jti(token: str) -> Optional[str]:
        """
        Extract JTI from a token.
        
        Args:
            token: JWT token string
            
        Returns:
            JTI or None if invalid
        """
        payload, error = JWTUtils.decode_token(token)
        if payload:
            return payload.get('jti')
        return None
    
    @staticmethod
    def extract_token_from_header(auth_header: str) -> Optional[str]:
        """
        Extract token from Authorization header.
        
        Args:
            auth_header: Authorization header value
            
        Returns:
            Token string or None
        """
        if not auth_header:
            return None
        
        parts = auth_header.split()
        
        if len(parts) != 2:
            return None
        
        if parts[0].lower() != 'bearer':
            return None
        
        return parts[1]
