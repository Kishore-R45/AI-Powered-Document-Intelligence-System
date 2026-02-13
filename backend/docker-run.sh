#!/bin/bash
# Quick start script for local Docker testing before HF deployment

echo "🚀 Building InfoVault Docker image..."
docker build -t infovault-backend .

echo ""
echo "✅ Build complete! Starting container..."
echo ""

# Run with environment variables from .env file
docker run -p 7860:7860 \
  --env-file .env \
  --name infovault-api \
  infovault-backend

# To stop: docker stop infovault-api
# To remove: docker rm infovault-api
# To view logs: docker logs infovault-api
