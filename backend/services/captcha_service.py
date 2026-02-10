"""
Captcha verification service.
Supports Google reCAPTCHA.
"""

import requests
from config import Config


class CaptchaService:
    """Captcha verification service."""
    
    @staticmethod
    def verify(token: str, remote_ip: str = None) -> tuple[bool, str]:
        """
        Verify a captcha token.
        
        Args:
            token: Captcha token from frontend
            remote_ip: Client IP address (optional)
            
        Returns:
            Tuple of (success, error_message)
        """
        if not Config.CAPTCHA_SECRET_KEY:
            # Captcha not configured - allow in development
            return True, None
        
        if not token:
            return False, "Captcha token is required"
        
        try:
            payload = {
                'secret': Config.CAPTCHA_SECRET_KEY,
                'response': token,
            }
            
            if remote_ip:
                payload['remoteip'] = remote_ip
            
            response = requests.post(Config.CAPTCHA_VERIFY_URL, data=payload, timeout=10)
            result = response.json()
            
            if result.get('success'):
                return True, None
            
            # Get error codes
            error_codes = result.get('error-codes', [])
            if 'timeout-or-duplicate' in error_codes:
                return False, "Captcha expired. Please try again."
            elif 'invalid-input-response' in error_codes:
                return False, "Invalid captcha. Please try again."
            else:
                return False, "Captcha verification failed. Please try again."
                
        except requests.RequestException as e:
            print(f"Captcha verification error: {e}")
            return False, "Unable to verify captcha. Please try again."
