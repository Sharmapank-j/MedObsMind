# MedObsMind DNS Configuration for MedObsMind.in

## Required DNS Records

Configure these DNS records at your domain registrar (e.g., GoDaddy, Namecheap, etc.):

### A Records (Point to your server IP)

```
Type    Name                Value (Your Server IP)    TTL
----    ----                ----------------------    ---
A       @                   YOUR_SERVER_IP            3600
A       www                 YOUR_SERVER_IP            3600
A       api                 YOUR_SERVER_IP            3600
A       admin               YOUR_SERVER_IP            3600
```

### Example (replace with your actual IP):

```
Type    Name                Value                     TTL
----    ----                -----                     ---
A       @                   203.0.113.1               3600
A       www                 203.0.113.1               3600
A       api                 203.0.113.1               3600
A       admin               203.0.113.1               3600
```

This will create:
- **medobsmind.in** → Main website
- **www.medobsmind.in** → Main website (www version)
- **api.medobsmind.in** → API endpoint
- **admin.medobsmind.in** → Admin panel

## SSL Certificate Setup

After DNS propagates (usually 1-24 hours), install SSL certificate:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate for all domains
sudo certbot --nginx \
  -d medobsmind.in \
  -d www.medobsmind.in \
  -d api.medobsmind.in \
  -d admin.medobsmind.in

# Certificate will auto-renew every 90 days
```

## Verification

### Check DNS Propagation

```bash
# Check A record
nslookup medobsmind.in

# Or use online tool
# https://dnschecker.org
```

### Test Domains

```bash
# Test main domain
curl http://medobsmind.in

# Test API
curl http://api.medobsmind.in/health

# After SSL setup:
curl https://medobsmind.in
curl https://api.medobsmind.in/health
```

## Registrar-Specific Instructions

### GoDaddy
1. Login to GoDaddy
2. Go to "My Products" → "Domains"
3. Click "DNS" next to your domain
4. Click "Add" to create A records
5. Set Name, Type (A), Value (your IP), TTL (3600)

### Namecheap
1. Login to Namecheap
2. Go to "Domain List" → Manage
3. Click "Advanced DNS"
4. Click "Add New Record"
5. Set Type (A Record), Host (@, www, api, admin), Value (your IP)

### Cloudflare (Recommended for CDN)
1. Sign up at cloudflare.com
2. Add site: medobsmind.in
3. Copy nameservers
4. Update nameservers at your registrar
5. In Cloudflare DNS, add A records
6. Enable "Proxied" (orange cloud) for CDN
7. SSL/TLS mode: "Full (Strict)"

Benefits of Cloudflare:
- Free SSL certificate
- Global CDN (faster worldwide)
- DDoS protection
- Caching
- Analytics

## After DNS Setup

Once DNS propagates:

1. SSL will work automatically
2. HTTPS will be enforced
3. HTTP will redirect to HTTPS
4. Your domains will be:
   - https://medobsmind.in
   - https://www.medobsmind.in
   - https://api.medobsmind.in
   - https://admin.medobsmind.in

## Troubleshooting

### DNS not resolving
- Wait 24 hours for propagation
- Clear DNS cache: `sudo systemd-resolve --flush-caches`
- Check with: `nslookup medobsmind.in`

### SSL certificate errors
```bash
# Check nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Reissue certificate
sudo certbot --nginx --force-renewal
```

### Can't access website
```bash
# Check if server is accessible
ping medobsmind.in

# Check if ports are open
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## Support

For DNS/domain issues:
- Email: support@medobsmind.in
- GitHub: https://github.com/Sharmapank-j/MedObsMind/issues
