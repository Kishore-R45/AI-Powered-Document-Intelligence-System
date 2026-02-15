"""
Application configuration module.
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
    
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/infovault')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'dev-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # AWS S3
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
    AWS_S3_REGION = os.getenv('AWS_S3_REGION', 'us-east-1')
    S3_PRESIGNED_URL_EXPIRY = 3600  # 1 hour
    
    # Pinecone
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    PINECONE_ENV = os.getenv('PINECONE_ENV')
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'infovault-docs')
    
    # Hugging Face
    HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
    
    # Email SMTP
    EMAIL_SMTP_HOST = os.getenv('EMAIL_SMTP_HOST', 'smtp.gmail.com')
    EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', 587))
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'InfoVault')
    
    # Captcha
    CAPTCHA_SECRET_KEY = os.getenv('CAPTCHA_SECRET_KEY')
    CAPTCHA_VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'
    
    # OTP Settings
    OTP_EXPIRY_MINUTES = 10
    OTP_LENGTH = 6
    
    # File Upload
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'webp'}
    
    # AI Models
    EMBEDDING_MODEL = 'sentence-transformers/all-mpnet-base-v2'  # 768-dim, superior quality
    QA_MODEL = 'meta-llama/Llama-3.1-8B-Instruct'  # Local model via transformers
    
    # RAG Configuration
    CHUNK_SIZE = 800       # Characters per chunk
    CHUNK_OVERLAP = 200    # Overlap between chunks
    RAG_TOP_K = 8          # Chunks to retrieve
    RAG_SCORE_THRESHOLD = 0.3  # Minimum similarity score
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/infovault_test'


def get_config():
    """Get configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    return configs.get(env, DevelopmentConfig)
