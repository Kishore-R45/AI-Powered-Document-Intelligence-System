"""
Mobile App Backend Configuration.
Loads environment variables and provides configuration classes.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask
    SECRET_KEY = os.getenv('JWT_SECRET', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # MongoDB (NEW cluster for mobile app)
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/infovault_mobile')
    
    # JWT - Extended expiry for mobile persistent sessions
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'dev-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)   # Mobile sessions last 30 days
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=90)  # Refresh tokens last 90 days
    JWT_BIOMETRIC_TOKEN_EXPIRES = timedelta(days=365)  # Biometric tokens last 1 year
    
    # Session auto-lock after 5 minutes of inactivity (checked client-side)
    SESSION_AUTO_LOCK_MINUTES = 5
    
    # Trusted device token expiry
    TRUSTED_DEVICE_EXPIRY_DAYS = 365
    
    # Pinecone (NEW index for mobile app)
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ENV = os.getenv('PINECONE_ENV')
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'infovault-mobile-docs')
    
    # Hugging Face
    HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
    
    # Email SMTP (same sending ID as website)
    EMAIL_SMTP_HOST = os.getenv('EMAIL_SMTP_HOST', 'smtp.gmail.com')
    EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', 587))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'InfoVault')
    
    # Firebase Cloud Messaging (FCM)
    FIREBASE_CREDENTIALS_JSON = os.getenv('FIREBASE_CREDENTIALS_JSON', '')
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
    
    # OTP Settings
    OTP_EXPIRY_MINUTES = 10
    OTP_LENGTH = 6
    
    # File Upload (mobile supports camera scan too)
    MAX_CONTENT_LENGTH = 15 * 1024 * 1024  # 15MB for camera photos
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'webp'}
    
    # AI Models
    EMBEDDING_MODEL = 'sentence-transformers/all-mpnet-base-v2'  # 768-dim
    QA_MODEL = 'meta-llama/Llama-3.1-8B-Instruct'
    
    # RAG Configuration
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 200
    RAG_TOP_K = 8
    RAG_SCORE_THRESHOLD = 0.3
    
    # Data Extraction - Key-value pairs from documents
    # Categories for automatic extraction
    EXTRACTION_CATEGORIES = {
        'id': ['pan', 'aadhaar', 'passport', 'license', 'voter_id', 'registration'],
        'academic': ['cgpa', 'sgpa', 'marks', 'grade', 'semester', 'degree', 'university', 'college'],
        'financial': ['amount', 'salary', 'income', 'tax', 'balance', 'account'],
        'personal': ['name', 'father', 'mother', 'dob', 'address', 'phone', 'email'],
        'insurance': ['policy', 'premium', 'coverage', 'nominee', 'claim'],
        'medical': ['diagnosis', 'prescription', 'doctor', 'hospital', 'blood_group'],
    }
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/infovault_mobile_test'


def get_config():
    """Get configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    return configs.get(env, DevelopmentConfig)
