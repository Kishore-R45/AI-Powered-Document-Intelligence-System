# InfoVault Backend

Enterprise-grade personal document management system backend.

## Features

- **Secure Authentication**: Email + OTP verification, JWT tokens, session management
- **Document Management**: Upload, view, delete with S3 storage
- **Vector Search**: Pinecone-powered semantic document search
- **Extractive QA**: Zero-hallucination question answering using RoBERTa
- **Notifications**: Document expiry reminders, activity notifications
- **Audit Logging**: Complete activity tracking

## Tech Stack

- **Framework**: Flask
- **Database**: MongoDB
- **Storage**: AWS S3
- **Vector DB**: Pinecone
- **AI Models**: 
  - Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
  - QA: `deepset/roberta-base-squad2`

## Setup

### Prerequisites

- Python 3.10+
- MongoDB
- AWS S3 bucket
- Pinecone account
- Tesseract OCR (optional, for image text extraction)

### Installation

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the application:
   ```bash
   # Development
   flask run --debug

   # or
   python app.py
   ```

### Environment Variables

```
MONGO_URI=mongodb://localhost:27017/infovault
JWT_SECRET=your-secret-key
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET_NAME=...
PINECONE_API_KEY=...
PINECONE_ENV=...
HUGGINGFACE_TOKEN=...
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=...
EMAIL_PASSWORD=...
CAPTCHA_SECRET_KEY=...
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/verify-otp` - Verify email OTP
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout
- `POST /auth/refresh` - Refresh token

### Documents
- `POST /documents/upload` - Upload document
- `GET /documents/list` - List all documents
- `GET /documents/<id>` - Get document details
- `GET /documents/view/<id>` - Get view URL
- `DELETE /documents/delete/<id>` - Delete document

### Chat (Question Answering)
- `POST /chat/query` - Ask a question
- `GET /chat/history` - Get chat history

### Dashboard
- `GET /dashboard/stats` - Get dashboard statistics
- `GET /dashboard/expiring` - Get expiring documents
- `GET /dashboard/timeline` - Get expiry timeline

### Notifications
- `GET /notifications` - List notifications
- `POST /notifications/<id>/read` - Mark as read
- `POST /notifications/read-all` - Mark all as read

### User
- `GET /user/profile` - Get profile
- `PUT /user/profile` - Update profile
- `POST /user/change-password` - Change password
- `POST /user/logout-all` - Logout all sessions

## Production Deployment

Using Gunicorn:
```bash
gunicorn wsgi:app -w 4 -b 0.0.0.0:5000
```

## Architecture

```
backend/
├── app.py              # Main application entry
├── config.py           # Configuration
├── wsgi.py            # WSGI entry point
├── models/            # MongoDB models
├── routes/            # API blueprints
├── services/          # Business logic
├── utils/             # Utilities
└── jobs/              # Background jobs
```

## Security Features

- Password hashing with bcrypt
- JWT with session tracking
- Rate limiting ready
- CORS configuration
- Input validation
- SQL injection prevention (MongoDB)
- XSS prevention in responses
- Audit logging

## Zero Hallucination Guarantee

The QA system uses **extractive** question answering only:
- Answers are exact spans from documents
- No generative AI for facts
- Returns "Not found in document" when uncertain
- All answers include source references
