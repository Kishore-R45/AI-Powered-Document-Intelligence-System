# 🚀 Quick Deployment Checklist - Hugging Face Spaces

## Before You Start
- [ ] MongoDB Atlas cluster created and connection string ready
- [ ] AWS S3 bucket created with access credentials
- [ ] Pinecone index created (384 dimensions, cosine metric)
- [ ] Hugging Face account and API token obtained
- [ ] Email SMTP credentials ready (Gmail app password)
- [ ] (Optional) Google reCAPTCHA secret key

## Files Created for HF Deployment
- ✅ `Dockerfile` - Container configuration
- ✅ `.dockerignore` - Excluded files
- ✅ `README.space.md` - Space documentation
- ✅ `DEPLOYMENT_HUGGINGFACE.md` - Complete guide
- ✅ `docker-run.sh` / `docker-run.ps1` - Local testing scripts

## Deployment Steps (5 minutes)

### 1. Create HF Space
```bash
# Go to: https://huggingface.co/new-space
# SDK: Docker
# Visibility: Your choice
```

### 2. Push Code
```bash
cd backend
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
git add .
git commit -m "Deploy to HF Spaces"
git push space main
```

### 3. Add Secrets (in Space Settings → Repository secrets)
```
JWT_SECRET=your-secret-key-min-32-chars
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/infovault
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET_NAME=your-bucket
AWS_S3_REGION=us-east-1
PINECONE_API_KEY=...
PINECONE_ENV=us-east-1-aws
PINECONE_INDEX_NAME=infovault-docs
HUGGINGFACE_TOKEN=hf_...
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=app-password
FLASK_ENV=production
CORS_ORIGINS=https://your-frontend.vercel.app
```

### 4. Wait for Build (5-10 min)
Watch the "Logs" tab for progress

### 5. Test API
```bash
# Your API URL: https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space
curl https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/health
```

### 6. Update Frontend
```env
# frontend/.env
VITE_API_BASE_URL=https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/api
```

## Test Locally First (Optional)
```bash
# Make sure Docker is running
./docker-run.sh        # Linux/Mac
# or
./docker-run.ps1       # Windows

# Test at http://localhost:7860/health
```

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Build timeout | Reduce dependencies or upgrade Space |
| MongoDB connection fails | Check MONGO_URI and whitelist 0.0.0.0/0 |
| S3 access denied | Verify AWS credentials and bucket permissions |
| CORS errors | Add frontend URL to CORS_ORIGINS secret |
| Models loading slow | First load caches models (1-2 min) |
| Space goes to sleep | Upgrade to persistent or send periodic requests |

## Environment Variables Quick Reference

### Critical (Must Have)
- `JWT_SECRET` - Auth security
- `MONGO_URI` - Database
- `AWS_*` - File storage (3 vars)
- `PINECONE_*` - Vector search (2-3 vars)
- `HUGGINGFACE_TOKEN` - AI models
- `EMAIL_*` - Notifications (2 vars)

### Important (Production)
- `FLASK_ENV=production`
- `CORS_ORIGINS` - Frontend URLs

### Optional
- `CAPTCHA_SECRET_KEY` - Bot protection
- `PORT` - Default 7860 (auto-set)

## Port Configuration
- **HF Spaces**: Port 7860 (default, auto-configured)
- **Local Docker**: Port 7860 (mapped to localhost:7860)
- **Local Flask**: Port 5000 (when running `python app.py`)

## Need Help?
- Full guide: `DEPLOYMENT_HUGGINGFACE.md`
- HF Docs: https://huggingface.co/docs/hub/spaces
- Support: Your Space's Discussions tab

---
**Expected build time**: 5-10 minutes for first deployment
**Expected runtime memory**: ~2-4 GB (depends on model usage)
**Cost**: FREE on HF Spaces with limitations

🎉 Once deployed, your API will be live at `https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space`
