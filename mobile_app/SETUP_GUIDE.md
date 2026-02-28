# InfoVault Mobile App - Backend Connection Setup Guide

## Architecture Overview

```
┌──────────────────┐     HTTPS/REST     ┌──────────────────────────────┐
│  Flutter Mobile   │ ←─────────────────→ │  Flask Backend (HF Spaces)   │
│  App (Frontend)   │                     │  Port 7860 / Docker          │
└──────────────────┘                     └──────────┬───────────────────┘
                                                    │
                                 ┌──────────────────┼──────────────────┐
                                 │                  │                  │
                            MongoDB Atlas      AWS S3           Pinecone
                            (User/Doc data)   (File storage)   (Vector DB)
```

## Step 1: Deploy the Backend on HuggingFace Spaces

Follow the detailed guide: **[backend/DEPLOYMENT_HUGGINGFACE.md](../backend/DEPLOYMENT_HUGGINGFACE.md)**

Quick summary:
1. Create a HuggingFace Space (Docker SDK)
2. Push the `backend/` folder contents to the Space
3. Set all required environment variables (Secrets):

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGO_URI` | MongoDB Atlas connection string | ✅ |
| `JWT_SECRET` | Random secret key for JWT tokens | ✅ |
| `AWS_ACCESS_KEY_ID` | AWS IAM access key | ✅ |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key | ✅ |
| `AWS_S3_BUCKET_NAME` | S3 bucket name for documents | ✅ |
| `AWS_S3_REGION` | S3 bucket region | ✅ |
| `PINECONE_API_KEY` | Pinecone vector DB API key | ✅ |
| `PINECONE_ENV` | Pinecone environment | ✅ |
| `PINECONE_INDEX_NAME` | Pinecone index name (default: `infovault-docs`) | ✅ |
| `HUGGINGFACE_TOKEN` | HF token for LLM access | ✅ |
| `EMAIL_USERNAME` | Email sender address | ⚡ For OTP |
| `EMAIL_PASSWORD` | Email app password | ⚡ For OTP |
| `RESEND_API_KEY` | Resend.com API key (recommended over SMTP) | ⚡ For OTP |
| `RECAPTCHA_SECRET_KEY` | Google reCAPTCHA secret | Optional |

4. Wait for the Space to build and start
5. Your backend URL will be: `https://<username>-<space-name>.hf.space`

## Step 2: Connect the Mobile App

Open `lib/api/api_config.dart` and update the `baseUrl`:

```dart
// Replace with your actual HuggingFace Space URL
static const String baseUrl = 'https://your-username-infovault-api.hf.space';
```

### For Local Development

If running the backend locally:

```dart
// Android Emulator
static const String baseUrl = 'http://10.0.2.2:7860';

// Physical Android device (use your PC's local IP)
static const String baseUrl = 'http://192.168.x.x:7860';

// iOS Simulator / Web
static const String baseUrl = 'http://localhost:7860';
```

To run the backend locally:
```bash
cd backend
pip install -r requirements.txt
python app.py
```

## Step 3: Build & Run the Mobile App

```bash
cd mobile_app/frontend

# Install dependencies
flutter pub get

# Run on connected device
flutter run

# Or build a release APK
flutter build apk --release
```

## API Endpoints Summary

All endpoints are prefixed with `/api`:

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/verify-otp` | Verify email OTP |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| POST | `/api/auth/forgot-password` | Request password reset |
| POST | `/api/auth/verify-reset-otp` | Verify reset OTP |
| POST | `/api/auth/reset-password` | Set new password |

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents/upload` | Upload document (multipart) |
| GET | `/api/documents/list` | List all user documents |
| GET | `/api/documents/:id` | Get document details + view URL |
| DELETE | `/api/documents/delete/:id` | Delete a document |

### AI Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/query` | Ask question about documents |
| GET | `/api/chat/history` | Get chat history |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Dashboard statistics |
| GET | `/api/dashboard/expiring` | Expiring documents |
| GET | `/api/dashboard/expired` | Expired documents |

### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications` | List notifications |
| POST | `/api/notifications/:id/read` | Mark as read |
| POST | `/api/notifications/read-all` | Mark all as read |
| DELETE | `/api/notifications/:id` | Delete notification |

### User Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user/profile` | Get profile |
| PUT | `/api/user/profile` | Update profile |
| POST | `/api/user/change-password` | Change password |

## Features Working End-to-End

| Feature | Mobile Screen | Backend Route | Status |
|---------|--------------|---------------|--------|
| User Signup | SignupScreen | POST /auth/signup | ✅ |
| Email OTP Verification | OTPVerificationScreen | POST /auth/verify-otp | ✅ |
| Resend OTP | OTPVerificationScreen | POST /auth/signup (resend) | ✅ |
| Login | LoginScreen | POST /auth/login | ✅ |
| Logout | ProfileScreen, AppDrawer | POST /auth/logout | ✅ |
| Forgot Password (full flow) | ForgotPasswordScreen | POST /auth/forgot-password → verify-reset-otp → reset-password | ✅ |
| Change Password | ProfileScreen, SettingsScreen | POST /user/change-password | ✅ |
| Edit Profile | ProfileScreen | PUT /user/profile | ✅ |
| Upload Document (real file) | UploadScreen | POST /documents/upload | ✅ |
| List Documents | DocumentsScreen | GET /documents/list | ✅ |
| View Document (opens URL) | DocumentViewerScreen | GET /documents/:id | ✅ |
| Delete Document | DocumentViewerScreen | DELETE /documents/delete/:id | ✅ |
| AI Chat (Q&A) | ChatScreen | POST /chat/query | ✅ |
| Chat History | ChatScreen | GET /chat/history | ✅ |
| Clear Chat | ChatScreen | DELETE /chat/history | ✅ |
| Notifications | NotificationsScreen | GET /notifications | ✅ |
| Mark Read | NotificationsScreen | POST /notifications/:id/read | ✅ |
| Mark All Read | NotificationsScreen | POST /notifications/read-all | ✅ |
| Delete Notification | NotificationsScreen | DELETE /notifications/:id | ✅ |
| Dashboard Stats | DashboardScreen | local from documents list | ✅ |
| Extracted Data | ExtractedDataScreen | derived from documents | ✅ |
| Dark Mode | SettingsScreen | local (ThemeProvider) | ✅ |
| Biometric Login | SettingsScreen | local (local_auth) | ✅ |

## Troubleshooting

### "Connection refused" / "Socket exception"
- Verify `baseUrl` in `api_config.dart` is correct
- Ensure the backend Space is running (not sleeping)
- For physical devices, use your PC's LAN IP (not `localhost`)

### "401 Unauthorized"
- Token may have expired — the app auto-clears and returns to login
- Check JWT_SECRET is properly set in HF Space secrets

### Upload fails
- Check S3 credentials are valid
- Ensure the S3 bucket allows upload from the backend
- File size limit is 10MB by default

### OTP emails not arriving
- HF Spaces blocks SMTP ports — use Resend API instead
- Check EMAIL_USERNAME / RESEND_API_KEY in Space secrets
- Check spam folder

### AI Chat not responding
- Verify HUGGINGFACE_TOKEN is set and valid
- Verify PINECONE_API_KEY and index are configured
- Upload at least one document first — chat searches indexed documents
