# MedObsMind - Complete Deployment Guide

## 🚀 Quick Start Deployment

### Option 1: Website Only (Fastest - 5 minutes)

The MedObsMind landing page is automatically deployed to GitHub Pages.

**Access:** https://sharmapank-j.github.io/MedObsMind

**Custom Domain (Optional):**
1. Purchase domain: `medobsmind.ai`
2. Add CNAME record: `sharmapank-j.github.io`
3. Configure in GitHub Settings → Pages → Custom domain

### Option 2: Complete Stack (Local/VPS - 15 minutes)

#### Prerequisites
- Ubuntu 20.04+ or similar Linux
- 8 GB RAM minimum
- 20 GB disk space
- Docker & Docker Compose installed

#### Quick Deploy Script

```bash
# 1. Clone repository
git clone https://github.com/Sharmapank-j/MedObsMind.git
cd MedObsMind

# 2. Configure environment
cp backend/.env.example backend/.env
nano backend/.env  # Edit with your settings

# 3. Deploy with Docker
docker-compose up -d

# 4. Check status
docker-compose ps

# Access:
# - Website: http://localhost:80
# - API: http://localhost:8000
# - Admin: http://localhost:8000/admin
```

### Option 3: Cloud Deployment (Production - 20 minutes)

#### AWS EC2 Deployment

```bash
# 1. Launch EC2 instance (t3.medium or larger)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu

# 4. Clone and deploy
git clone https://github.com/Sharmapank-j/MedObsMind.git
cd MedObsMind
cp backend/.env.example backend/.env
# Edit .env with production settings
docker-compose -f docker-compose.prod.yml up -d

# 5. Configure security group (AWS Console)
# - Allow port 80 (HTTP)
# - Allow port 443 (HTTPS)
# - Allow port 22 (SSH)

# 6. Set up domain
# - Point your domain to instance IP
# - Configure SSL with Let's Encrypt (see below)
```

#### DigitalOcean Droplet Deployment

```bash
# 1. Create droplet (2 GB RAM minimum)
# 2. SSH into droplet
ssh root@your-droplet-ip

# 3. One-line installer
curl -fsSL https://raw.githubusercontent.com/Sharmapank-j/MedObsMind/main/scripts/install.sh | bash

# Access: http://your-droplet-ip
```

---

## 📦 Deployment Methods

### Method 1: GitHub Pages (Website Only)

**Status:** ✅ AUTOMATED

- **Platform:** GitHub Pages
- **Cost:** FREE
- **URL:** https://sharmapank-j.github.io/MedObsMind
- **Deploy Time:** 2-3 minutes (automatic)
- **SSL:** Automatic (GitHub provides)

**How it works:**
1. Push to `main` branch
2. GitHub Actions automatically deploys
3. Changes live in 2-3 minutes

### Method 2: Docker Compose (Full Stack)

**Status:** ✅ READY

Components deployed:
- ✅ Backend API (FastAPI)
- ✅ PostgreSQL Database
- ✅ Redis Cache
- ✅ Nginx Reverse Proxy

**File:** `docker-compose.yml`

```yaml
services:
  backend:
    # FastAPI application
    ports: 8000
  
  postgres:
    # PostgreSQL database
    
  redis:
    # Redis cache
    
  nginx:
    # Reverse proxy
    ports: 80, 443
```

**Commands:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update and restart
git pull
docker-compose up -d --build
```

### Method 3: Kubernetes (Enterprise Scale)

**Status:** 📋 Documentation Available

For large-scale deployments (100+ hospitals):
- Horizontal scaling
- Load balancing
- High availability
- Auto-healing

See: `docs/KUBERNETES_DEPLOYMENT.md`

### Method 4: Serverless (Cost-Optimized)

**Status:** 📋 Documentation Available

Deploy backend as serverless functions:
- **AWS Lambda** + API Gateway
- **Google Cloud Functions**
- **Azure Functions**

See: `docs/SERVERLESS_DEPLOYMENT.md`

---

## 🔐 SSL/HTTPS Setup

### Option 1: Let's Encrypt (Free)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d medobsmind.ai -d www.medobsmind.ai

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

### Option 2: Cloudflare (Free + CDN)

1. Sign up at cloudflare.com
2. Add your domain
3. Update nameservers
4. Enable "Full (Strict)" SSL
5. Enable "Always Use HTTPS"

**Benefits:**
- Free SSL
- Global CDN
- DDoS protection
- Caching

---

## 🌍 Production Environment Setup

### Environment Variables

Create `backend/.env` with:

```bash
# Application
DEBUG=False
SECRET_KEY=your-secret-key-here-change-this
ALLOWED_HOSTS=medobsmind.ai,www.medobsmind.ai

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/medobsmind
REDIS_URL=redis://redis:6379/0

# AI Models
MODEL_PATH=/models/dsquaremedicalmodel-q4_k_m.gguf
MODEL_CACHE_DIR=/models/cache

# External Services
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

### Database Setup

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Load initial data (optional)
docker-compose exec backend python manage.py loaddata initial_data.json
```

### Model Setup

```bash
# Download dsquaremedicalmodel
docker-compose exec backend python scripts/download_model.py

# Or manually:
mkdir -p models
cd models
wget https://huggingface.co/d2media/dsquaremedicalmodel/resolve/main/dsquaremedicalmodel-q4_k_m.gguf
```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check all services
docker-compose ps

# Check API health
curl http://localhost:8000/health

# Check database
docker-compose exec postgres pg_isready

# Check Redis
docker-compose exec redis redis-cli ping
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Backups

```bash
# Backup database
docker-compose exec postgres pg_dump -U medobsmind medobsmind > backup.sql

# Backup with Docker volume
docker run --rm \
  -v medobsmind_postgres_data:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/postgres-backup-$(date +%Y%m%d).tar.gz /data

# Automated daily backups
# Add to crontab:
0 2 * * * cd /path/to/MedObsMind && ./scripts/backup.sh
```

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Run new migrations
docker-compose exec backend python manage.py migrate
```

---

## 🚦 Deployment Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] Database credentials set
- [ ] SSL certificates ready
- [ ] Domain DNS configured
- [ ] Google OAuth credentials obtained
- [ ] Backup strategy implemented

### Deployment
- [ ] Services started successfully
- [ ] Database migrations applied
- [ ] Admin user created
- [ ] Models downloaded
- [ ] Health checks passing

### Post-Deployment
- [ ] Website accessible
- [ ] API responding
- [ ] SSL working (HTTPS)
- [ ] Database queries working
- [ ] AI model inference working
- [ ] Monitoring configured
- [ ] Backups scheduled

### Testing
- [ ] User registration works
- [ ] Google OAuth login works
- [ ] Patient data entry works
- [ ] Vitals recording works
- [ ] Alert generation works
- [ ] AI recommendations work
- [ ] Multi-language works

---

## 🆘 Troubleshooting

### Website not accessible
```bash
# Check nginx
docker-compose logs nginx

# Check if port is open
sudo netstat -tulpn | grep :80

# Restart nginx
docker-compose restart nginx
```

### API errors
```bash
# Check backend logs
docker-compose logs backend

# Check if backend is running
docker-compose ps backend

# Restart backend
docker-compose restart backend
```

### Database connection errors
```bash
# Check PostgreSQL
docker-compose logs postgres

# Check connection
docker-compose exec postgres psql -U medobsmind -c "SELECT 1"

# Restart database
docker-compose restart postgres
```

### Model loading errors
```bash
# Check model exists
docker-compose exec backend ls -lh /models/

# Check model integrity
docker-compose exec backend python -c "from llama_cpp import Llama; Llama(model_path='/models/dsquaremedicalmodel-q4_k_m.gguf')"

# Re-download model
docker-compose exec backend python scripts/download_model.py --force
```

---

## 🔄 Continuous Deployment

### GitHub Actions (Automated)

Every push to `main` branch automatically:
1. ✅ Runs tests
2. ✅ Builds Docker images
3. ✅ Deploys to staging (optional)
4. ✅ Deploys website to GitHub Pages

**Configure secrets in GitHub:**
```
Settings → Secrets and Variables → Actions

Add:
- DOCKER_USERNAME
- DOCKER_PASSWORD
- AWS_ACCESS_KEY_ID (if using AWS)
- AWS_SECRET_ACCESS_KEY
```

### Manual Deployment

```bash
# Tag a release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# GitHub Actions will automatically build and deploy
```

---

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Update nginx config for load balancing
# (See docker-compose.prod.yml)
```

### Database Scaling

```bash
# Enable read replicas
# Add to docker-compose.yml:
postgres-replica:
  image: postgres:14
  environment:
    POSTGRESQL_MASTER_HOST: postgres
    POSTGRESQL_REPLICATION_MODE: slave
```

### Caching

```bash
# Configure Redis for session storage
# Configure CDN for static assets
# Enable database query caching
```

---

## 🌟 Production Best Practices

1. **Use HTTPS only** - Redirect HTTP to HTTPS
2. **Enable monitoring** - Sentry, Prometheus, Grafana
3. **Configure backups** - Daily automated backups
4. **Set up alerts** - Email/Slack for critical errors
5. **Use CDN** - Cloudflare for static assets
6. **Enable logging** - Centralized log management
7. **Security headers** - HSTS, CSP, X-Frame-Options
8. **Rate limiting** - Protect against abuse
9. **Health checks** - Automated uptime monitoring
10. **Documentation** - Keep deployment docs updated

---

## 📞 Support

**Deployment Issues:**
- GitHub Issues: https://github.com/Sharmapank-j/MedObsMind/issues
- Email: support@medobsmind.ai

**Documentation:**
- Complete docs: https://github.com/Sharmapank-j/MedObsMind/tree/main/docs
- API docs: http://your-domain/api/docs

**Community:**
- Discord: (Coming soon)
- Slack: (Coming soon)

---

## 🎉 Deployment Complete!

Your MedObsMind installation is now live! 

**Next Steps:**
1. Access admin panel: http://your-domain/admin
2. Create first hospital
3. Add first users
4. Configure medical guidelines
5. Start monitoring patients

**Thank you for deploying MedObsMind! 🏥💙**

---

**Last Updated:** February 6, 2026  
**Version:** 1.0.0  
**Maintainer:** d²media
