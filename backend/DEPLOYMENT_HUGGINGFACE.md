# InfoVault Backend - Hugging Face Spaces Deployment Guide

## Prerequisites

1. **Hugging Face Account**: Sign up at [huggingface.co](https://huggingface.co)
2. **External Services**:
   - MongoDB Atlas account (free tier available)
   - AWS S3 bucket for document storage
   - Pinecone account for vector database
   - Gmail account or SMTP service for emails
   - Google reCAPTCHA keys (optional)

## Step 1: Prepare Your Services

### MongoDB Atlas
1. Create a free cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a database user
3. Whitelist all IPs (`0.0.0.0/0`) for HF Spaces
4. Get your connection string (looks like `mongodb+srv://...`)

### AWS S3
1. Create an S3 bucket in AWS Console
2. Enable public access settings if needed
3. Create IAM user with S3 access
4. Save Access Key ID and Secret Access Key
5. Note your bucket name and region

### Pinecone
1. Sign up at [pinecone.io](https://www.pinecone.io)
2. Create an index named `infovault-docs`
   - Dimensions: **384** (for all-MiniLM-L6-v2)
   - Metric: cosine
3. Get your API key and environment from the console

### Hugging Face Token
1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create a new token with `read` permissions
3. Save the token securely

### Email SMTP
For Gmail:
1. Enable 2-factor authentication
2. Generate an App Password: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Use your Gmail address and app password

### Google reCAPTCHA (Optional)
1. Go to [google.com/recaptcha/admin](https://www.google.com/recaptcha/admin)
2. Register a new site (reCAPTCHA v2)
3. Save the secret key

## Step 2: Create Hugging Face Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in the details:
   - **Space name**: `infovault-api` (or your choice)
   - **License**: MIT
   - **Space SDK**: Docker
   - **Visibility**: Public or Private
3. Click "Create Space"

## Step 3: Push Backend Code to Space

### Option A: Using Git (Recommended)

```bash
cd backend

# Initialize git if not already done
git init

# Add HF Space as remote (replace USERNAME/SPACE_NAME)
git remote add space https://huggingface.co/spaces/USERNAME/SPACE_NAME
git add .
git commit -m "Initial deployment"

# Push to HF Space
git push space main
```

### Option B: Using Web UI

1. Upload these files to your Space via the "Files" tab:
   - `Dockerfile`
   - `requirements.txt`
   - `app.py`
   - `config.py`
   - `wsgi.py`
   - All folders: `models/`, `routes/`, `services/`, `utils/`, `jobs/`
   - `README.space.md` (will appear as Space README)

## Step 4: Configure Environment Variables

In your Space settings, add these as **Secrets** (Settings → Repository secrets):

### Required Secrets

```bash
JWT_SECRET=your-super-secret-jwt-key-here-min-32-chars
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/infovault?retryWrites=true&w=majority

# AWS S3
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET_NAME=your-bucket-name
AWS_S3_REGION=us-east-1

# Pinecone
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENV=us-east-1-aws
PINECONE_INDEX_NAME=infovault-docs

# Hugging Face
HUGGINGFACE_TOKEN=hf_...

# Email (Gmail example)
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM_NAME=InfoVault

# Flask
FLASK_ENV=production
PORT=7860
```

### Optional Secrets

```bash
# Google reCAPTCHA (if using)
CAPTCHA_SECRET_KEY=6LdtUWos...

# CORS - Add your frontend URL
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
```

## Step 5: Deploy and Monitor

1. **Trigger Build**: After pushing code or updating secrets, the Space will rebuild
2. **Monitor Build Logs**: Check the "Logs" tab for build progress
3. **Wait for Deployment**: First build takes 5-10 minutes (downloading models)
4. **Access API**: Your API will be at `https://USERNAME-SPACE_NAME.hf.space`

### Test Your Deployment

```bash
# Health check
curl https://USERNAME-SPACE_NAME.hf.space/health

# API root
curl https://USERNAME-SPACE_NAME.hf.space/

# Expected responses:
# {"status":"healthy","service":"infovault-api"}
# {"name":"InfoVault API","version":"1.0.0","status":"running"}
```

## Step 6: Update Frontend

Update your frontend `.env` to point to the HF Space URL:

```env
VITE_API_BASE_URL=https://USERNAME-SPACE_NAME.hf.space/api
```

## Troubleshooting

### Build Fails

**Issue**: Out of memory during build
- **Solution**: Reduce model size or use CPU-only torch

**Issue**: Timeout during build
- **Solution**: HF Spaces has build timeout limits. Optimize dependencies.

### Runtime Errors

**Issue**: MongoDB connection fails
- **Solution**: Check MONGO_URI is correct and IPs are whitelisted (0.0.0.0/0)

**Issue**: AWS S3 access denied
- **Solution**: Verify IAM permissions and credentials are correct

**Issue**: Pinecone errors
- **Solution**: Ensure index dimensions match model (384 for all-MiniLM-L6-v2)

**Issue**: CORS errors from frontend
- **Solution**: Add frontend URL to CORS_ORIGINS secret

### Performance

**Issue**: Slow first response (cold start)
- **Solution**: Keep Space active or upgrade to persistent deployment

**Issue**: Model loading timeout
- **Solution**: Hugging Face models cache after first load

## Space Settings

### Hardware (Free Tier)
- 16 GB RAM
- 2 CPU cores
- No persistent storage (use external DB/S3)

### Automatic Sleep
Free Spaces sleep after 48h inactivity. Upgrade to prevent sleep.

### Custom Domain (Pro)
Available with HF Pro subscription.

## Maintenance

### View Logs
```bash
# Real-time logs in HF Space UI
# Or clone and check locally
git clone https://huggingface.co/spaces/USERNAME/SPACE_NAME
```

### Update Code
```bash
cd backend
git add .
git commit -m "Update feature X"
git push space main
```

### Rollback
```bash
git revert HEAD
git push space main
```

## Security Best Practices

1. ✅ Never commit `.env` files
2. ✅ Use HF Spaces Secrets for sensitive data
3. ✅ Rotate JWT_SECRET regularly
4. ✅ Enable reCAPTCHA in production
5. ✅ Use strong MongoDB credentials
6. ✅ Restrict S3 bucket access
7. ✅ Monitor API usage and rate limits

## Cost Estimates

- **Hugging Face Space**: Free (with limitations) or $5/month (Pro)
- **MongoDB Atlas**: Free 512MB or $0.08/GB after
- **AWS S3**: ~$0.023/GB storage + transfer costs
- **Pinecone**: Free 1GB or ~$70/month (1M vectors)
- **Hugging Face Inference**: Free for public models

## Support

- HF Spaces Docs: [huggingface.co/docs/hub/spaces](https://huggingface.co/docs/hub/spaces)
- Community: [discuss.huggingface.co](https://discuss.huggingface.co)
- Issues: Report in your Space's discussions

---

**Ready to deploy? Follow the steps above and your InfoVault backend will be live on Hugging Face Spaces! 🚀**
