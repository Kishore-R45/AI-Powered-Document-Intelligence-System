"""
Firebase Cloud Messaging service for push notifications.
Handles FCM token management and push notification delivery.
"""

import os
import json
from typing import List, Optional
from config import Config


class FirebaseService:
    """Firebase Cloud Messaging service for mobile push notifications."""
    
    _initialized = False
    _app = None
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK."""
        if cls._initialized:
            return
        
        try:
            import firebase_admin
            from firebase_admin import credentials
            
            # Try JSON credentials from environment variable
            creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
            
            if creds_json:
                try:
                    creds_dict = json.loads(creds_json)
                    cred = credentials.Certificate(creds_dict)
                    cls._app = firebase_admin.initialize_app(cred)
                    cls._initialized = True
                    print("[Firebase] Initialized with JSON credentials")
                    return
                except json.JSONDecodeError as e:
                    print(f"[Firebase] Invalid JSON credentials: {e}")
            
            # Try credentials file path
            creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            if creds_path and os.path.exists(creds_path):
                cred = credentials.Certificate(creds_path)
                cls._app = firebase_admin.initialize_app(cred)
                cls._initialized = True
                print(f"[Firebase] Initialized with credentials file: {creds_path}")
                return
            
            # Try default credentials (for Google Cloud environments)
            try:
                cls._app = firebase_admin.initialize_app()
                cls._initialized = True
                print("[Firebase] Initialized with default credentials")
                return
            except Exception:
                pass
            
            print("[Firebase] WARNING: No Firebase credentials found. Push notifications disabled.")
            print("[Firebase] Set FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS_PATH")
            
        except ImportError:
            print("[Firebase] firebase-admin not installed. Push notifications disabled.")
        except Exception as e:
            print(f"[Firebase] Initialization error: {e}")
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if Firebase is initialized and available."""
        return cls._initialized
    
    @classmethod
    def send_to_device(cls, fcm_token: str, title: str, body: str, data: dict = None) -> bool:
        """
        Send push notification to a single device.
        
        Args:
            fcm_token: FCM registration token
            title: Notification title
            body: Notification body text
            data: Optional data payload
            
        Returns:
            True if sent successfully
        """
        if not cls._initialized:
            print("[Firebase] Not initialized, skipping push notification")
            return False
        
        try:
            from firebase_admin import messaging
            
            notification = messaging.Notification(
                title=title,
                body=body
            )
            
            # Build message
            message = messaging.Message(
                notification=notification,
                token=fcm_token,
                data=data or {},
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        click_action='FLUTTER_NOTIFICATION_CLICK',
                        channel_id='infovault_notifications',
                        priority='high',
                        default_sound=True,
                    )
                ),
            )
            
            response = messaging.send(message)
            print(f"[Firebase] Sent to device: {response}")
            return True
            
        except Exception as e:
            error_str = str(e)
            if 'NOT_FOUND' in error_str or 'UNREGISTERED' in error_str:
                print(f"[Firebase] Token invalid/expired: {fcm_token[:20]}...")
                return False
            print(f"[Firebase] Send error: {e}")
            return False
    
    @classmethod
    def send_multicast(cls, fcm_tokens: List[str], title: str, body: str, data: dict = None) -> dict:
        """
        Send push notification to multiple devices.
        
        Args:
            fcm_tokens: List of FCM registration tokens
            title: Notification title
            body: Notification body text
            data: Optional data payload
            
        Returns:
            Dict with 'success_count', 'failure_count', 'failed_tokens'
        """
        if not cls._initialized:
            return {'success_count': 0, 'failure_count': len(fcm_tokens), 'failed_tokens': fcm_tokens}
        
        if not fcm_tokens:
            return {'success_count': 0, 'failure_count': 0, 'failed_tokens': []}
        
        try:
            from firebase_admin import messaging
            
            notification = messaging.Notification(
                title=title,
                body=body
            )
            
            message = messaging.MulticastMessage(
                notification=notification,
                tokens=fcm_tokens,
                data=data or {},
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        click_action='FLUTTER_NOTIFICATION_CLICK',
                        channel_id='infovault_notifications',
                        priority='high',
                        default_sound=True,
                    )
                ),
            )
            
            response = messaging.send_each_for_multicast(message)
            
            failed_tokens = []
            for i, send_response in enumerate(response.responses):
                if not send_response.success:
                    failed_tokens.append(fcm_tokens[i])
            
            result = {
                'success_count': response.success_count,
                'failure_count': response.failure_count,
                'failed_tokens': failed_tokens
            }
            
            print(f"[Firebase] Multicast: {result['success_count']} sent, {result['failure_count']} failed")
            return result
            
        except Exception as e:
            print(f"[Firebase] Multicast error: {e}")
            return {'success_count': 0, 'failure_count': len(fcm_tokens), 'failed_tokens': fcm_tokens}
    
    @classmethod
    def send_to_user(cls, user_id: str, title: str, body: str, data: dict = None) -> bool:
        """
        Send push notification to all devices of a user.
        
        Args:
            user_id: User's ID
            title: Notification title
            body: Notification body text
            data: Optional data payload
            
        Returns:
            True if at least one notification was sent
        """
        if not cls._initialized:
            return False
        
        try:
            from models.user import User
            
            fcm_tokens = User.get_fcm_tokens(user_id)
            
            if not fcm_tokens:
                print(f"[Firebase] No FCM tokens for user {user_id}")
                return False
            
            if len(fcm_tokens) == 1:
                return cls.send_to_device(fcm_tokens[0], title, body, data)
            
            result = cls.send_multicast(fcm_tokens, title, body, data)
            
            # Clean up invalid tokens
            if result['failed_tokens']:
                for token in result['failed_tokens']:
                    User.remove_fcm_token(user_id, token)
                    print(f"[Firebase] Removed invalid token for user {user_id}")
            
            return result['success_count'] > 0
            
        except Exception as e:
            print(f"[Firebase] Error sending to user {user_id}: {e}")
            return False
    
    @classmethod
    def send_document_notification(cls, user_id: str, document_name: str, notification_type: str = 'upload') -> bool:
        """Send document-related push notification."""
        titles = {
            'upload': 'Document Uploaded',
            'processed': 'Document Processed',
            'expiring': 'Document Expiring Soon',
            'expired': 'Document Expired',
        }
        
        bodies = {
            'upload': f'"{document_name}" has been uploaded successfully.',
            'processed': f'"{document_name}" has been processed. Extracted data is ready.',
            'expiring': f'"{document_name}" is expiring soon. Please take action.',
            'expired': f'"{document_name}" has expired.',
        }
        
        title = titles.get(notification_type, 'Document Update')
        body = bodies.get(notification_type, f'Update for "{document_name}"')
        
        data = {
            'type': 'document',
            'action': notification_type,
            'document_name': document_name,
        }
        
        return cls.send_to_user(user_id, title, body, data)
    
    @classmethod
    def send_expiry_reminder(cls, user_id: str, document_name: str, days_remaining: int) -> bool:
        """Send document expiry reminder push notification."""
        if days_remaining <= 0:
            title = "Document Expired"
            body = f'"{document_name}" has expired. Please renew it.'
        elif days_remaining == 1:
            title = "Document Expires Tomorrow!"
            body = f'"{document_name}" expires tomorrow. Take action now.'
        elif days_remaining <= 7:
            title = "Document Expiring Soon"
            body = f'"{document_name}" expires in {days_remaining} days.'
        else:
            title = "Document Expiry Reminder"
            body = f'"{document_name}" expires in {days_remaining} days.'
        
        data = {
            'type': 'expiry_reminder',
            'document_name': document_name,
            'days_remaining': str(days_remaining),
        }
        
        return cls.send_to_user(user_id, title, body, data)
