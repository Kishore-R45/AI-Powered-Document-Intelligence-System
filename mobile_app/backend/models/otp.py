"""
OTP (One-Time Password) model for email verification.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Optional

from models import mongo
from config import Config


class OTP:
    """OTP model for email verification."""
    
    collection_name = 'otps'
    
    @staticmethod
    def generate_code(length: int = 6) -> str:
        """Generate a random numeric OTP code."""
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def create(email: str) -> dict:
        """Create a new OTP for the given email."""
        email = email.lower().strip()
        
        mongo.db.otps.delete_many({'email': email})
        
        code = OTP.generate_code(Config.OTP_LENGTH)
        expires_at = datetime.utcnow() + timedelta(minutes=Config.OTP_EXPIRY_MINUTES)
        
        otp_doc = {
            'email': email,
            'code': code,
            'attempts': 0,
            'created_at': datetime.utcnow(),
            'expires_at': expires_at,
        }
        
        result = mongo.db.otps.insert_one(otp_doc)
        otp_doc['_id'] = result.inserted_id
        return otp_doc
    
    @staticmethod
    def verify(email: str, code: str) -> tuple[bool, str]:
        """Verify an OTP code."""
        email = email.lower().strip()
        
        otp_doc = mongo.db.otps.find_one({'email': email})
        
        if not otp_doc:
            return False, 'No verification code found. Please request a new one.'
        
        if datetime.utcnow() > otp_doc['expires_at']:
            mongo.db.otps.delete_one({'_id': otp_doc['_id']})
            return False, 'Verification code has expired. Please request a new one.'
        
        if otp_doc.get('attempts', 0) >= 5:
            mongo.db.otps.delete_one({'_id': otp_doc['_id']})
            return False, 'Too many failed attempts. Please request a new verification code.'
        
        mongo.db.otps.update_one(
            {'_id': otp_doc['_id']},
            {'$inc': {'attempts': 1}}
        )
        
        if otp_doc['code'] != code:
            return False, 'Invalid verification code. Please try again.'
        
        mongo.db.otps.delete_one({'_id': otp_doc['_id']})
        return True, 'Email verified successfully.'
    
    @staticmethod
    def delete_for_email(email: str) -> int:
        """Delete all OTPs for a given email."""
        result = mongo.db.otps.delete_many({'email': email.lower().strip()})
        return result.deleted_count
