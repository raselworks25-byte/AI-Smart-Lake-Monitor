# 🚀 Deployment Guide - Smart AI Lake Monitoring System

This guide covers deploying your Flask application to various hosting platforms.

---

## ✅ **Pre-Deployment Checklist**

Before deploying to any platform:

- [ ] Copy `.env.example` to `.env` and fill in all required values
- [ ] Set a strong `SECRET_KEY` (e.g., `python -c 'import secrets; print(secrets.token_hex(32))'`)
- [ ] Set a strong `INGEST_API_KEY` for Raspberry Pi uploads
- [ ] Configure Firebase credentials (if using Firebase)
- [ ] Run locally with production settings: `FLASK_ENV=production FLASK_DEBUG=false python app.py`
- [ ] Ensure all dependencies are in requirements.txt
- [ ] Test API endpoints: `curl -H "X-INGEST-TOKEN: your-api-key" http://localhost:5000/api/overview`

---

## 📋 **Environment Variables (Required)**

Set these on your hosting platform:

```bash
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=<generate-strong-random-key>
INGEST_API_KEY=<your-secure-api-key>
PORT=5000
```

### Optional (Firebase):
```bash
FIREBASE_DATABASE_URL=https://your-project.firebasedatabase.app/
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json
```

---

## 🏠 **Option 1: Heroku (Easiest)**

### Setup:
```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create your-lake-monitoring-app

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=false
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
heroku config:set INGEST_API_KEY=your-secure-api-key

# Deploy
git push heroku main
```

### Notes:
- Free tier available (512MB RAM)
- Automatic SSL/HTTPS
- Scales easily
- Firebase compatible

---

## 🐳 **Option 2: Docker + Any Cloud (AWS, Google Cloud, Azure, DigitalOcean)**

### Create Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
```

### Create .dockerignore:
```
.git
.gitignore
__pycache__
*.pyc
.venv
venv
.env
Web_LIVE_Image
```

### Build & Run Locally:
```bash
# Build image
docker build -t lake-monitoring:latest .

# Run locally
docker run -p 5000:5000 \
  -e SECRET_KEY=test-key \
  -e INGEST_API_KEY=test-api-key \
  lake-monitoring:latest
```

### Deploy to DigitalOcean App Platform:
```bash
doctl apps create --spec app.yaml
```

Or Docker Hub + DigitalOcean Container Registry:
```bash
docker push your-registry/lake-monitoring:latest
```

---

## ☁️ **Option 3: DigitalOcean Droplet (Full Control)**

### 1. Create Droplet (Ubuntu 22.04):
```bash
# SSH into droplet
ssh root@your-droplet-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3.11 python3-pip python3-venv nginx supervisor git

# Clone repository
cd /home && git clone your-repo-url
cd flooting_boat
```

### 2. Setup Python environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Create Supervisor config (`/etc/supervisor/conf.d/lake-monitoring.conf`):
```ini
[program:lake-monitoring]
directory=/home/flooting_boat
command=/home/flooting_boat/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/lake-monitoring.log
environment=FLASK_ENV=production,FLASK_DEBUG=false,SECRET_KEY=your-key,INGEST_API_KEY=your-key
```

### 4. Setup Nginx (`/etc/nginx/sites-available/lake-monitoring`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /home/flooting_boat/static;
    }
}
```

### 5. Enable and restart:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start lake-monitoring

sudo systemctl restart nginx

# Setup HTTPS
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 🚀 **Option 4: Railway (Dead Simple)**

### 1. Connect GitHub:
- Go to railway.app
- Connect your GitHub repository
- Railway auto-detects Python project

### 2. Set Environment Variables in Railway Dashboard:
```
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=<your-key>
INGEST_API_KEY=<your-key>
```

### 3. Railway auto-deploys on every git push

---

## 🚀 **Option 5: AWS Elastic Beanstalk**

### 1. Create `.ebextensions/python.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: wsgi:app
  aws:elasticbeanstalk:application:environment:
    FLASK_ENV: production
    FLASK_DEBUG: "false"
```

### 2. Deploy:
```bash
pip install awseb-cli
eb create lake-monitoring-env
eb deploy
```

---

## 🔧 **Testing Your Deployment**

```bash
# Test login page
curl https://your-domain.com/login

# Test API (requires X-INGEST-TOKEN header)
curl -X POST https://your-domain.com/api/ingest/water \
  -H "X-INGEST-TOKEN: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"tds": 150, "turbidity": 5.2, "temperature": 28.5}'

# Check logs (Heroku)
heroku logs --tail

# Check logs (DigitalOcean)
sudo tail -f /var/log/lake-monitoring.log
```

---

## 📊 **Recommended Setup (Best for This Project)**

**For Quick Start**: Heroku or Railway
- ✅ Easiest setup
- ✅ Auto HTTPS
- ✅ Minimal DevOps
- ❌ Limited customization
- ❌ Paid after free tier

**For Production**: DigitalOcean App Platform or Droplet
- ✅ Full control
- ✅ Affordable ($5-12/month)
- ✅ Docker support
- ✅ Good performance
- ❌ Needs basic Linux knowledge

**For Scale**: AWS or Google Cloud
- ✅ Unlimited scale
- ✅ Advanced monitoring
- ❌ Complex setup
- ❌ Expensive ($30+/month)

---

## 🐛 **Common Issues & Solutions**

### Issue: "ModuleNotFoundError: No module named 'cv2'"
**Solution**: OpenCV is optional. Install system libraries or use headless version in cloud.

### Issue: Firebase credentials not found
**Solution**: Upload credentials file or use `GOOGLE_APPLICATION_CREDENTIALS` env var pointing to mounted path.

### Issue: Port already in use
**Solution**: Use PORT environment variable or change default port in `wsgi.py`

### Issue: Static files not loading
**Solution**: Run `python -m flask --app app collect-static` or configure nginx to serve `/static`

---

## 🔐 **Security Checklist**

- [ ] SECRET_KEY is 32+ random characters
- [ ] INGEST_API_KEY is strong and unique
- [ ] FLASK_DEBUG is `false`
- [ ] Running behind HTTPS
- [ ] Weak user passwords updated (admin/research/viewer accounts)
- [ ] Firebase credentials never committed to git
- [ ] .env file in .gitignore
- [ ] Regular backups configured

---

## 📞 **Support**

For platform-specific issues:
- Heroku: https://devcenter.heroku.com/articles/getting-started-with-python
- Railway: https://docs.railway.app/
- DigitalOcean: https://docs.digitalocean.com/
- AWS: https://docs.aws.amazon.com/elasticbeanstalk/
