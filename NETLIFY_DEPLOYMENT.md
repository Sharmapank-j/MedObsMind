# Netlify Deployment Guide for MedObsMind

## 🚀 Quick Deploy to Netlify

### Option 1: One-Click Deploy (Recommended)

Click the button below to deploy MedObsMind to Netlify:

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/Sharmapank-j/MedObsMind)

### Option 2: Manual Deployment via Netlify UI

1. **Sign in to Netlify**
   - Go to [https://app.netlify.com](https://app.netlify.com)
   - Sign in or create account (free tier available)

2. **Import Project**
   - Click "Add new site" → "Import an existing project"
   - Connect to GitHub
   - Select `Sharmapank-j/MedObsMind` repository

3. **Configure Build Settings**
   - **Branch to deploy:** `main` (or `copilot/create-medobsmind-landing-page` for testing)
   - **Build command:** (leave empty - static site)
   - **Publish directory:** `.` (root directory)
   - Click "Deploy site"

4. **Wait for Deployment**
   - First deployment takes 1-2 minutes
   - Netlify will provide a URL like: `https://random-name-123.netlify.app`

5. **Custom Domain (Optional)**
   - Go to Site settings → Domain management
   - Add custom domain: `medobsmind.netlify.app` or `medobsmind.in`
   - Configure DNS records as instructed

### Option 3: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize site
netlify init

# Deploy
netlify deploy --prod
```

---

## 📁 Configuration Files

### netlify.toml
Main configuration file with:
- Build settings
- Security headers
- Redirect rules
- Performance optimizations
- Environment variables

### _redirects
URL redirect rules:
- API proxying
- Custom domain redirects
- 404 handling

### robots.txt
SEO configuration:
- Allow search engines
- Sitemap locations
- Crawl settings

---

## 🔧 Configuration Details

### Build Settings

```toml
[build]
  command = "echo 'Building MedObsMind website...'"
  publish = "."
  base = "/"
```

- **No build command needed** - static HTML/CSS/JS
- **Publish directory:** Current directory (contains index.html)

### Security Headers

Automatic headers for all pages:
- ✅ X-Frame-Options: DENY
- ✅ X-Content-Type-Options: nosniff
- ✅ X-XSS-Protection: 1; mode=block
- ✅ Content-Security-Policy
- ✅ Referrer-Policy

### Performance Optimizations

- CSS/JS minification
- Image compression
- Asset caching (1 year for static assets)
- HTML pretty URLs
- Gzip compression

### API Proxying

Requests to `/api/*` are proxied to:
```
https://api.medobsmind.in
```

This avoids CORS issues and maintains clean URLs.

---

## 🌐 Deployment URLs

### After Deployment

**Netlify Default URL:**
```
https://[your-site-name].netlify.app
```

**Custom Domain (Optional):**
```
https://medobsmind.in
https://www.medobsmind.in
https://medobsmind.netlify.app
```

**GitHub Pages (Parallel):**
```
https://sharmapank-j.github.io/MedObsMind
```

---

## 🔄 Continuous Deployment

### Automatic Deployments

Netlify automatically deploys when:
- ✅ Push to main branch
- ✅ Pull request created (deploy preview)
- ✅ Branch pushed (branch deploy)

### Deploy Previews

Every pull request gets a unique preview URL:
```
https://deploy-preview-[pr-number]--[site-name].netlify.app
```

### Branch Deploys

Each branch gets its own URL:
```
https://[branch-name]--[site-name].netlify.app
```

---

## 🛠️ Environment Variables

Add in Netlify UI (Site settings → Environment variables):

```bash
# Google OAuth (if needed)
GOOGLE_OAUTH_CLIENT_ID=your_client_id

# API Endpoint
API_ENDPOINT=https://api.medobsmind.in

# Custom variables
SITE_NAME=MedObsMind
SITE_URL=https://medobsmind.in
```

---

## 📊 Monitoring & Analytics

### Netlify Analytics

Enable in: Site settings → Analytics
- Page views
- Top pages
- Traffic sources
- Geographic data

### Custom Analytics (Optional)

Add to `index.html`:
- Google Analytics
- Plausible Analytics (privacy-friendly)
- Simple Analytics

---

## 🔒 Security Features

### HTTPS

- ✅ Automatic SSL certificate (Let's Encrypt)
- ✅ Auto-renewal every 90 days
- ✅ Force HTTPS redirect

### Headers

All security headers configured in `netlify.toml`:
- Content Security Policy
- XSS Protection
- Frame Options
- Content Type Options

### DDoS Protection

- Built-in DDoS mitigation
- Rate limiting
- Bot protection

---

## 🚨 Troubleshooting

### Deployment Fails

**Check:**
1. Build logs in Netlify dashboard
2. netlify.toml syntax
3. File paths are correct
4. No Git conflicts

**Common Issues:**
- Missing files: Ensure all referenced files exist
- Build errors: Check build logs
- 404 errors: Verify publish directory

### Site Not Loading

**Check:**
1. DNS settings (if using custom domain)
2. SSL certificate status
3. Deploy status (should be "Published")
4. Browser cache (try incognito mode)

### Redirects Not Working

**Check:**
1. `_redirects` file is in publish directory
2. Syntax is correct (no trailing spaces)
3. Order matters (first match wins)
4. Force flag (!) if needed

---

## 📈 Performance Optimization

### Current Setup

- ✅ CSS/JS minification enabled
- ✅ Image compression enabled
- ✅ Asset caching (1 year)
- ✅ Gzip compression automatic
- ✅ HTTP/2 enabled
- ✅ Global CDN

### Further Optimizations (Optional)

1. **Add Service Worker** for offline support
2. **Lazy load images** for faster initial load
3. **Preload critical resources**
4. **Enable Brotli compression**

---

## 🔗 Useful Links

**Netlify Dashboard:**
- https://app.netlify.com/sites/[your-site-name]

**Documentation:**
- [Netlify Docs](https://docs.netlify.com)
- [Redirects](https://docs.netlify.com/routing/redirects/)
- [Headers](https://docs.netlify.com/routing/headers/)
- [Forms](https://docs.netlify.com/forms/setup/)

**Support:**
- [Netlify Community](https://answers.netlify.com)
- [Status Page](https://www.netlifystatus.com)

---

## ✅ Deployment Checklist

### Before Deployment

- [x] netlify.toml created
- [x] _redirects file created
- [x] robots.txt added
- [x] index.html present
- [x] styles.css present
- [x] script.js present
- [x] All assets in place

### After Deployment

- [ ] Site loads correctly
- [ ] All pages accessible
- [ ] CSS/JS working
- [ ] Redirects working
- [ ] HTTPS active
- [ ] Custom domain configured (if applicable)
- [ ] Analytics enabled (optional)

### Testing

- [ ] Test on desktop
- [ ] Test on mobile
- [ ] Test different browsers
- [ ] Check console for errors
- [ ] Verify links work
- [ ] Test forms (if any)

---

## 🎉 Success!

Once deployed, your site will be available at:

**Netlify URL:** `https://[your-site-name].netlify.app`

Share with the world! 🌍

---

© 2026 d²media | MedObsMind.in

**Need help?** Open an issue on GitHub or contact support@medobsmind.in
