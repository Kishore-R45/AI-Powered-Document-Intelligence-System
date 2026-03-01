# InfoVault Mobile Backend - Deployment Guide

## Overview
Separate Flask backend for the InfoVault mobile app (Flutter). Deployed to a **new HuggingFace Space** independent of the web backend.

## Key Differences from Web Backend
| Feature | Web Backend | Mobile Backend |
|---------|------------|----------------|
| File Storage | AWS S3 | None (local on device) |
| Push Notifications | None | Firebase Cloud Messaging |
| Biometric Auth | None | Trusted device + biometric tokens |
| Data Extraction | None | AI key-value extraction |
| JWT Access Token | 7 days | 30 days |
| JWT Refresh Token | 30 days | 90 days |
| Biometric Token | N/A | 365 days |
| Session Auto-Lock | N/A | 5 minutes |
| Captcha | reCAPTCHA | None |
| Pinecone Index | `infovault-docs` | `infovault-mobile-docs` |

## Prerequisites
1. **New MongoDB Cluster** - Separate database for mobile users
2. **New Pinecone Index** - `infovault-mobile-docs` (dimension: 768, metric: cosine)
3. **Firebase Project** - For push notifications (FCM)
4. **HuggingFace Account** - For deployment
5. **Brevo Account** - Same as web backend (shared email service)

## Setup

### 1. Create Pinecone Index
```python
import pinecone
pc = pinecone.Pinecone(api_key="YOUR_KEY")
pc.create_index(
    name="infovault-mobile-docs",
    dimension=768,
    metric="cosine",
    spec=pinecone.ServerlessSpec(cloud="aws", region="us-east-1")
)
```

### 2. Firebase Setup
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use existing
3. Go to **Project Settings > Service Accounts**
4. Generate a new private key (JSON)
5. Either:
   - Set `FIREBASE_CREDENTIALS_JSON` env var with the JSON content
   - Or set `GOOGLE_APPLICATION_CREDENTIALS` to the file path

### 3. HuggingFace Spaces Deployment

#### Create New Space
1. Go to [HuggingFace Spaces](https://huggingface.co/spaces)
2. Create new Space with **Docker** SDK
3. Hardware: **CPU Basic** (free tier) or **CPU Upgrade** for better performance

#### Set Environment Variables
In the Space settings, add these secrets:
- `MONGODB_URI`
- `JWT_SECRET_KEY`
- `PINECONE_API_KEY`
- `HF_TOKEN`
- `BREVO_API_KEY`
- `BREVO_SENDER_EMAIL`
- `BREVO_SENDER_NAME`
- `FIREBASE_CREDENTIALS_JSON`
- `FIREBASE_PROJECT_ID`

#### Deploy
Push this entire `mobile_app/backend/` directory to the Space repo.

### 4. Local Development
```bash
cd mobile_app/backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
python app.py
```

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/verify-otp` | Verify email OTP |
| POST | `/api/auth/login` | Login with email/password |
| POST | `/api/auth/biometric-login` | Login with biometric |
| POST | `/api/auth/register-device` | Register trusted device |
| POST | `/api/auth/validate-session` | Validate session status |
| POST | `/api/auth/logout` | Logout current session |
| POST | `/api/auth/refresh` | Refresh token |
| POST | `/api/auth/forgot-password` | Initiate password reset |
| POST | `/api/auth/verify-reset-otp` | Verify reset OTP |
| POST | `/api/auth/reset-password` | Reset password |

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents/upload` | Upload & process document |
| GET | `/api/documents/list` | List all documents |
| GET | `/api/documents/<id>` | Get document details |
| GET | `/api/documents/<id>/extracted-data` | Get extracted key-value data |
| POST | `/api/documents/<id>/re-extract` | Re-run AI extraction |
| PUT | `/api/documents/<id>` | Update document metadata |
| DELETE | `/api/documents/delete/<id>` | Delete document |
| POST | `/api/documents/reindex` | Reindex all embeddings |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/query` | Ask question about documents |
| GET | `/api/chat/history` | Get chat history |
| DELETE | `/api/chat/history` | Clear chat history |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Get dashboard statistics |
| GET | `/api/dashboard/expiring` | Get expiring documents |
| GET | `/api/dashboard/expired` | Get expired documents |
| GET | `/api/dashboard/timeline` | Get expiry timeline |
| POST | `/api/dashboard/trigger-expiry-check` | Manual expiry check |

### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications` | List notifications |
| POST | `/api/notifications/<id>/read` | Mark as read |
| POST | `/api/notifications/read-all` | Mark all as read |
| DELETE | `/api/notifications/<id>` | Delete notification |
| GET | `/api/notifications/unread-count` | Get unread count |
| POST | `/api/notifications/register-fcm` | Register FCM token |
| POST | `/api/notifications/unregister-fcm` | Unregister FCM token |
| POST | `/api/notifications/test-push` | Send test push |

### User
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user/profile` | Get profile |
| PUT | `/api/user/profile` | Update profile |
| POST | `/api/user/change-password` | Change password |
| POST | `/api/user/logout-all` | Logout all sessions |
| POST | `/api/user/biometric/toggle` | Enable/disable biometric |
| GET | `/api/user/biometric/status` | Get biometric status |
| GET | `/api/user/sessions` | List active sessions |
| DELETE | `/api/user/sessions/<id>` | Revoke a session |
| GET | `/api/user/trusted-devices` | List trusted devices |
| DELETE | `/api/user/trusted-devices/<id>` | Revoke trusted device |
| DELETE | `/api/user/trusted-devices` | Revoke all devices |
