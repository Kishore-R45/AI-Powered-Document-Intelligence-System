"""
Trusted device model for biometric authentication and persistent sessions.
"""

from datetime import datetime, timedelta
from bson import ObjectId
from typing import List

from models import mongo
from config import Config


class TrustedDevice:
    """Model for managing trusted devices for biometric login."""
    
    collection_name = 'trusted_devices'
    
    @staticmethod
    def register(
        user_id: str,
        device_id: str,
        device_name: str = None,
        device_model: str = None,
        os_version: str = None,
        biometric_type: str = None
    ) -> dict:
        """
        Register a device as trusted for biometric login.
        
        Args:
            user_id: User's ID
            device_id: Unique device identifier
            device_name: Human-readable device name
            device_model: Device model (e.g., 'Samsung Galaxy S24')
            os_version: OS version (e.g., 'Android 14')
            biometric_type: Type of biometric (fingerprint, face, iris)
        """
        # Remove existing registration for this device
        mongo.db.trusted_devices.delete_many({
            'user_id': ObjectId(user_id),
            'device_id': device_id
        })
        
        expires_at = datetime.utcnow() + timedelta(days=Config.TRUSTED_DEVICE_EXPIRY_DAYS)
        
        device = {
            'user_id': ObjectId(user_id),
            'device_id': device_id,
            'device_name': device_name or 'Unknown Device',
            'device_model': device_model,
            'os_version': os_version,
            'biometric_type': biometric_type or 'fingerprint',
            'is_active': True,
            'registered_at': datetime.utcnow(),
            'last_used': datetime.utcnow(),
            'expires_at': expires_at,
        }
        
        result = mongo.db.trusted_devices.insert_one(device)
        device['_id'] = result.inserted_id
        return device
    
    @staticmethod
    def find_by_device_id(user_id: str, device_id: str) -> dict | None:
        """Find a trusted device registration."""
        return mongo.db.trusted_devices.find_one({
            'user_id': ObjectId(user_id),
            'device_id': device_id,
            'is_active': True,
            'expires_at': {'$gt': datetime.utcnow()}
        })
    
    @staticmethod
    def is_trusted(user_id: str, device_id: str) -> bool:
        """Check if a device is trusted for biometric login."""
        device = TrustedDevice.find_by_device_id(user_id, device_id)
        return device is not None
    
    @staticmethod
    def update_last_used(user_id: str, device_id: str) -> bool:
        """Update the last used timestamp."""
        result = mongo.db.trusted_devices.update_one(
            {
                'user_id': ObjectId(user_id),
                'device_id': device_id,
                'is_active': True
            },
            {'$set': {'last_used': datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def get_user_devices(user_id: str) -> List[dict]:
        """Get all trusted devices for a user."""
        return list(mongo.db.trusted_devices.find({
            'user_id': ObjectId(user_id),
            'is_active': True,
            'expires_at': {'$gt': datetime.utcnow()}
        }).sort('last_used', -1))
    
    @staticmethod
    def revoke(user_id: str, device_id: str) -> bool:
        """Revoke a trusted device."""
        result = mongo.db.trusted_devices.update_one(
            {
                'user_id': ObjectId(user_id),
                'device_id': device_id
            },
            {'$set': {'is_active': False}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def revoke_all(user_id: str) -> int:
        """Revoke all trusted devices for a user."""
        result = mongo.db.trusted_devices.update_many(
            {'user_id': ObjectId(user_id), 'is_active': True},
            {'$set': {'is_active': False}}
        )
        return result.modified_count
    
    @staticmethod
    def to_dict(device: dict) -> dict:
        """Convert device to dictionary."""
        if not device:
            return None
        return {
            'id': str(device['_id']),
            'deviceId': device.get('device_id'),
            'deviceName': device.get('device_name'),
            'deviceModel': device.get('device_model'),
            'osVersion': device.get('os_version'),
            'biometricType': device.get('biometric_type'),
            'isActive': device.get('is_active', False),
            'registeredAt': device.get('registered_at').isoformat() if device.get('registered_at') else None,
            'lastUsed': device.get('last_used').isoformat() if device.get('last_used') else None,
            'expiresAt': device.get('expires_at').isoformat() if device.get('expires_at') else None,
        }
