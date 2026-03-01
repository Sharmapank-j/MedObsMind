# Security Policy

## Supported Versions

We take security seriously at MedObsMind. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We appreciate responsible disclosure of security vulnerabilities. 

### How to Report

**Please DO NOT create public GitHub issues for security vulnerabilities.**

Instead, please report security vulnerabilities to:
- **Email:** security@medobsmind.in
- **Subject:** [SECURITY] Brief description

### What to Include

Please include:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)
5. Your contact information

### Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial Assessment:** Within 1 week
- **Fix Timeline:** Depends on severity
  - Critical: 24-72 hours
  - High: 1 week
  - Medium: 2-4 weeks
  - Low: Next release

### Security Measures

MedObsMind implements multiple security layers:

#### Application Security
- ✅ Input validation & sanitization
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CSRF tokens
- ✅ Rate limiting
- ✅ Authentication (OAuth 2.0)
- ✅ Authorization (RBAC)
- ✅ Session management

#### Data Security
- ✅ Encryption at rest (AES-256)
- ✅ Encryption in transit (TLS 1.3)
- ✅ Database connection encryption
- ✅ Secure password hashing (bcrypt)
- ✅ PII anonymization
- ✅ GDPR & DPDP Act 2023 compliant

#### Infrastructure Security
- ✅ HTTPS only (Let's Encrypt)
- ✅ Security headers (CSP, HSTS, etc.)
- ✅ Firewall rules
- ✅ DDoS protection
- ✅ Regular security updates
- ✅ Automated backups

#### Medical Data Security
- ✅ HIPAA-aware architecture
- ✅ Audit logging
- ✅ Access controls
- ✅ Data retention policies
- ✅ Consent management

### Security Best Practices

If you're deploying MedObsMind:

1. **Change all default passwords**
2. **Use strong, unique passwords (32+ characters)**
3. **Enable MFA for admin accounts**
4. **Keep system updated**
5. **Configure firewall properly**
6. **Use HTTPS only**
7. **Regular backups**
8. **Monitor logs**
9. **Restrict SSH access**
10. **Use VPN for admin access**

### Known Security Considerations

As a medical AI platform:
- ⚠️ Not a medical device (informational only)
- ⚠️ Not FDA/CE certified
- ⚠️ Not a substitute for professional medical advice
- ⚠️ Users responsible for clinical decisions
- ⚠️ Deploy behind institutional firewall
- ⚠️ Regular security audits recommended

### Compliance

MedObsMind is designed for compliance with:
- GDPR (General Data Protection Regulation - EU)
- DPDP Act 2023 (India)
- HIPAA considerations (US)
- ISO 27001 principles
- OWASP Top 10 protections

### Third-Party Dependencies

We regularly audit dependencies for vulnerabilities:
- Automated: Dependabot (GitHub)
- Manual: Monthly security review
- Updates: Applied promptly

### Security Hall of Fame

We recognize security researchers who help us improve:
- (Your name here - report responsibly!)

### Contact

**Security Team:** security@medobsmind.in  
**Website:** https://medobsmind.in  
**PGP Key:** Available on request

---

Thank you for helping keep MedObsMind and our users safe!

© 2026 d²media | Governed by d³media
