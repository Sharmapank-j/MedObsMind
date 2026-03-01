# 🚀 MedObsMind - Quick Deployment Guide

## Domain: MedObsMind.in

### 🎯 Quick Deploy (15 minutes)

```bash
# One-line installer
curl -fsSL https://raw.githubusercontent.com/Sharmapank-j/MedObsMind/main/scripts/deploy.sh | sudo bash
```

That's it! MedObsMind will be deployed and running.

---

## 📋 What Gets Deployed

✅ **Website**: Main landing page  
✅ **API**: FastAPI backend  
✅ **Database**: PostgreSQL  
✅ **Cache**: Redis  
✅ **Reverse Proxy**: Nginx  

**Your domains:**
- https://medobsmind.in - Main website
- https://www.medobsmind.in - WWW version
- https://api.medobsmind.in - API endpoint
- https://admin.medobsmind.in - Admin panel

---

## 🌐 DNS Setup (Required)

**Point these domains to your server IP:**

```
Type    Name      Value (Your Server IP)
----    ----      ----------------------
A       @         YOUR_SERVER_IP
A       www       YOUR_SERVER_IP
A       api       YOUR_SERVER_IP  
A       admin     YOUR_SERVER_IP
```

**Example:** If your server IP is `203.0.113.1`:
- medobsmind.in → 203.0.113.1
- www.medobsmind.in → 203.0.113.1
- api.medobsmind.in → 203.0.113.1
- admin.medobsmind.in → 203.0.113.1

See [DNS_SETUP.md](DNS_SETUP.md) for detailed instructions.

---

## 🔒 SSL Certificate (After DNS Setup)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get FREE SSL certificate from Let's Encrypt
sudo certbot --nginx \
  -d medobsmind.in \
  -d www.medobsmind.in \
  -d api.medobsmind.in \
  -d admin.medobsmind.in

# Auto-renewal is configured automatically!
```

---

## ✅ Post-Deployment Steps

### 1. Create Admin User

```bash
cd /opt/MedObsMind
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

### 2. Download AI Model

```bash
docker-compose -f docker-compose.prod.yml exec backend python scripts/download_model.py
```

### 3. Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project → Enable APIs → OAuth consent screen
3. Create credentials → OAuth 2.0 Client ID
4. Add authorized redirect URIs:
   - https://medobsmind.in/auth/google/callback
   - https://api.medobsmind.in/auth/google/callback
5. Copy Client ID and Secret
6. Update `.env` file with credentials

### 4. Test Everything

```bash
# Check services
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Test API
curl https://api.medobsmind.in/health
```

---

## 🔧 Management Commands

### View Logs
```bash
cd /opt/MedObsMind
docker-compose -f docker-compose.prod.yml logs -f
```

### Restart Services
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Update to Latest Version
```bash
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```

### Backup Database
```bash
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U medobsmind medobsmind > backup-$(date +%Y%m%d).sql
```

### Stop Everything
```bash
docker-compose -f docker-compose.prod.yml down
```

---

## 📊 Access Your Deployment

After DNS propagates (1-24 hours):

- **Website**: https://medobsmind.in
- **API Docs**: https://api.medobsmind.in/docs
- **Admin Panel**: https://medobsmind.in/admin

---

## 🆘 Troubleshooting

### Website not accessible
```bash
# Check nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Check if port 80 is open
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Database errors
```bash
# Check PostgreSQL
docker-compose -f docker-compose.prod.yml logs postgres

# Restart database
docker-compose -f docker-compose.prod.yml restart postgres
```

### SSL certificate issues
```bash
# Test nginx config
sudo nginx -t

# Renew certificate
sudo certbot renew
```

---

## 📞 Need Help?

- **Documentation**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **DNS Setup**: [DNS_SETUP.md](DNS_SETUP.md)
- **GitHub Issues**: https://github.com/Sharmapank-j/MedObsMind/issues
- **Email**: support@medobsmind.in

---

## 🎉 You're All Set!

MedObsMind is now deployed and ready to transform healthcare!

**Next:** Start monitoring your first patients 🏥💙
