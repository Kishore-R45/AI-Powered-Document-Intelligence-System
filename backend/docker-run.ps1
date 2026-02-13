# Quick start script for local Docker testing before HF deployment (Windows)

Write-Host "🚀 Building InfoVault Docker image..." -ForegroundColor Cyan
docker build -t infovault-backend .

Write-Host ""
Write-Host "✅ Build complete! Starting container..." -ForegroundColor Green
Write-Host ""

# Run with environment variables from .env file
docker run -p 7860:7860 `
  --env-file .env `
  --name infovault-api `
  infovault-backend

# To stop: docker stop infovault-api
# To remove: docker rm infovault-api
# To view logs: docker logs infovault-api
