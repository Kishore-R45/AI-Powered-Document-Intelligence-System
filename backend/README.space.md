---
title: InfoVault API
emoji: 🔐
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# InfoVault API - Hugging Face Space

Enterprise-grade personal document management backend running on Hugging Face Spaces.

## Features

- 🔐 JWT-based authentication with OTP email verification
- 📄 Document upload & management (AWS S3)
- 🤖 AI-powered Q&A using RAG (Retrieval-Augmented Generation)
- 🔍 Semantic search with Pinecone vector database
- 📧 Email notifications for document expiry
- 🛡️ Google reCAPTCHA protection

## Environment Variables

Configure these secrets in your Hugging Face Space settings:

### Required
- `JWT_SECRET` - Secret key for JWT tokens
- `MONGO_URI` - MongoDB connection string
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_S3_BUCKET_NAME` - S3 bucket name
- `PINECONE_API_KEY` - Pinecone API key
- `PINECONE_ENV` - Pinecone environment
- `HUGGINGFACE_TOKEN` - HuggingFace API token
- `EMAIL_USERNAME` - SMTP email address
- `EMAIL_PASSWORD` - SMTP email password

### Optional
- `CAPTCHA_SECRET_KEY` - Google reCAPTCHA secret key
- `CORS_ORIGINS` - Comma-separated allowed origins (default: localhost)
- `AWS_S3_REGION` - AWS region (default: us-east-1)
- `EMAIL_SMTP_HOST` - SMTP host (default: smtp.gmail.com)
- `EMAIL_SMTP_PORT` - SMTP port (default: 587)
- `PINECONE_INDEX_NAME` - Pinecone index name (default: infovault-docs)

## API Endpoints

- `GET /` - API root
- `GET /health` - Health check
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/verify-otp` - Email verification
- `GET /api/dashboard` - Dashboard statistics
- `POST /api/documents/upload` - Upload documents
- `GET /api/documents` - List user documents
- `POST /api/chat/query` - AI Q&A on documents

## Tech Stack

- **Framework**: Flask 3.0
- **Database**: MongoDB
- **Storage**: AWS S3
- **Vector DB**: Pinecone
- **AI Models**: 
  - Embeddings: sentence-transformers/all-MiniLM-L6-v2
  - LLM: meta-llama/Llama-3.1-8B-Instruct
- **Server**: Gunicorn

## License

MIT
