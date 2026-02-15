"""
Captcha verification service.
Supports Google reCAPTCHA.
Automatically skips verification for localhost/development.
"""

import requests
from config import Config


class CaptchaService:
    """Captcha verification service."""
    
    # IPs that are considered localhost
    LOCALHOST_IPS = {'127.0.0.1', '::1', 'localhost', '0.0.0.0', '10.0.0.0'}
    
    @staticmethod
    def is_localhost(remote_ip: str = None) -> bool:
        """
        Check if the request comes from localhost.
        
        Args:
            remote_ip: Client IP address
            
        Returns:
            True if localhost
        """
        if not remote_ip:
            return False
        return remote_ip in CaptchaService.LOCALHOST_IPS or remote_ip.startswith('127.') or remote_ip.startswith('192.168.') or remote_ip.startswith('10.')
    
    @staticmethod
    def verify(token: str, remote_ip: str = None) -> tuple[bool, str]:
        """
        Verify a captcha token.
        Automatically skips verification for localhost requests.
        
        Args:
            token: Captcha token from frontend
            remote_ip: Client IP address (optional)
            
        Returns:
            Tuple of (success, error_message)
        """
        # Skip captcha for localhost / development
        if CaptchaService.is_localhost(remote_ip):
            print(f"[Captcha] Skipping verification for localhost ({remote_ip})")
            return True, None
        
        if not Config.CAPTCHA_SECRET_KEY:
            # Captcha not configured - allow in development
            print("[Captcha] No CAPTCHA_SECRET_KEY configured, skipping verification")
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
            # On captcha service failure, allow the request through
            # rather than blocking legitimate users
            return True, None
