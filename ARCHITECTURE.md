# MedObsMind System Architecture

## Overview

MedObsMind is a comprehensive medical AI platform built with a microservices architecture, designed for scalability, reliability, and offline-first operation.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
├─────────────┬──────────────┬──────────────┬────────────────────┤
│ Web App     │ Android App  │ iOS App      │ Admin Dashboard    │
│ (React)     │ (Kotlin)     │ (Swift)      │ (React)            │
└─────────────┴──────────────┴──────────────┴────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Nginx Reverse Proxy                                            │
│  - Load Balancing                                               │
│  - SSL Termination                                              │
│  - Rate Limiting                                                │
│  - CORS Handling                                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                             │
├─────────────┬──────────────┬──────────────┬────────────────────┤
│ FastAPI     │ DDMA Agent   │ LLM Service  │ Multimodal AI      │
│ Backend     │ (Chat API)   │ (dsquaremd)  │ (Vision/Audio)     │
└─────────────┴──────────────┴──────────────┴────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Service Layer                                │
├─────────────┬──────────────┬──────────────┬────────────────────┤
│ Auth        │ Patient      │ Vitals       │ Alert              │
│ Service     │ Service      │ Service      │ Service            │
│             │              │              │                    │
│ User        │ AI/ML        │ Training     │ Export             │
│ Service     │ Service      │ Service      │ Service            │
└─────────────┴──────────────┴──────────────┴────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
├─────────────┬──────────────┬──────────────┬────────────────────┤
│ PostgreSQL  │ Redis        │ MinIO        │ Vector DB          │
│ (Primary DB)│ (Cache)      │ (Objects)    │ (RAG)              │
└─────────────┴──────────────┴──────────────┴────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Docker Containers | Kubernetes (optional) | Monitoring         │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Client Layer

#### Web Application (React)
- **Purpose:** Doctor/nurse interface for patient monitoring
- **Tech Stack:** React 18, TypeScript, Material-UI
- **Features:**
  - Real-time patient dashboard
  - Vitals entry & visualization
  - Alert management
  - AI recommendations
  - Multi-language support

#### Android Application (Kotlin)
- **Purpose:** Mobile access for bedside care
- **Tech Stack:** Kotlin, Jetpack Compose, MVVM
- **Features:**
  - Offline-first architecture
  - On-device AI inference
  - Camera integration (vitals)
  - Push notifications
  - Biometric authentication

#### iOS Application (Swift)
- **Purpose:** iOS device support
- **Tech Stack:** SwiftUI, Combine
- **Features:** Similar to Android
- **Integrations:** HealthKit, Core ML

#### Admin Dashboard
- **Purpose:** System management & monitoring
- **Features:**
  - User management
  - Hospital configuration
  - Model training control
  - System analytics
  - Audit logs

### 2. API Gateway Layer

#### Nginx Reverse Proxy
- **Functions:**
  - Load balancing across backend instances
  - SSL/TLS termination
  - Request routing
  - Rate limiting (10 req/s per IP)
  - Static file serving
  - Compression (gzip)
  - Security headers

**Configuration:**
```nginx
upstream backend {
    server backend:8000;
}

server {
    listen 443 ssl http2;
    server_name api.medobsmind.in;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/medobsmind.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/medobsmind.in/privkey.pem;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    
    location / {
        proxy_pass http://backend;
        # ... proxy settings
    }
}
```

### 3. Application Layer

#### FastAPI Backend
- **Purpose:** Core API server
- **Tech Stack:** Python 3.11, FastAPI, Pydantic
- **Endpoints:** 40+ REST APIs
- **Features:**
  - Async/await for concurrency
  - OpenAPI documentation
  - Request validation
  - JWT authentication
  - CORS handling

**Key Modules:**
```python
backend/
├── app/
│   ├── main.py              # Application entry
│   ├── config.py            # Configuration
│   ├── database.py          # DB connection
│   ├── api/                 # API endpoints
│   │   ├── auth.py
│   │   ├── patients.py
│   │   ├── vitals.py
│   │   ├── alerts.py
│   │   └── ai.py
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── patient_service.py
│   │   ├── vitals_service.py
│   │   └── ai_service.py
│   ├── models/              # Data models
│   │   ├── user.py
│   │   ├── patient.py
│   │   └── vitals.py
│   └── utils/               # Utilities
│       ├── security.py
│       ├── logging.py
│       └── helpers.py
└── tests/                   # Test suite
```

#### DDMA Agent (d²media Agent)
- **Purpose:** ChatGPT-compatible medical AI
- **API:** OpenAI-compatible `/v1/chat/completions`
- **Features:**
  - Conversational interface
  - Function calling (6 medical tools)
  - Streaming responses
  - Context management
  - Safety guardrails

#### LLM Service (dsquaremedicalmodel)
- **Purpose:** Medical language model inference
- **Model:** LLaMA-3 8B fine-tuned + LoRA
- **Format:** GGUF (4.5 GB, Q4_K_M)
- **Engine:** llama.cpp
- **Performance:** 2-3s inference on CPU
- **Context:** 8K tokens

#### Multimodal AI Service
- **Vision:**
  - X-ray analysis
  - ECG interpretation
  - Wound assessment
  - Medical diagram understanding
- **Audio:**
  - Heart sound analysis
  - Lung sound classification
  - Speech recognition (13 languages)
- **Integration:** Ensemble models

### 4. Service Layer

#### Authentication Service
- **Functions:**
  - Google OAuth integration
  - JWT token management
  - Session handling
  - MFA for admins
  - Role-based access control

#### Patient Service
- **Functions:**
  - Patient CRUD operations
  - Medical record management
  - Admission/discharge tracking
  - Data export

#### Vitals Service
- **Functions:**
  - Vitals recording
  - Trend analysis
  - NEWS2/qSOFA calculation
  - Alert generation
  - Historical data retrieval

#### Alert Service
- **Functions:**
  - Real-time alert generation
  - Escalation workflows
  - Alert acknowledgment
  - Notification delivery
  - Alert analytics

#### AI/ML Service
- **Functions:**
  - Model loading & management
  - Inference orchestration
  - Caching & optimization
  - Multi-model support
  - Performance monitoring

#### Training Service
- **Functions:**
  - Data collection & sanitization
  - LoRA training automation
  - Model conversion to GGUF
  - Quality assessment
  - Deployment automation

#### Export Service
- **Functions:**
  - Excel export
  - SQL dump generation
  - PostgreSQL export
  - CSV/JSON export
  - Backup management

### 5. Data Layer

#### PostgreSQL (Primary Database)
- **Purpose:** Structured data storage
- **Version:** 14+
- **Tables:**
  - users (authentication & profiles)
  - patients (patient records)
  - vitals (measurements)
  - alerts (alert history)
  - consents (user consents)
  - training_data_pool (ML training data)
  - audit_logs (system audit)

**Schema Design:**
```sql
-- Example: Vitals table
CREATE TABLE vitals (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    timestamp TIMESTAMP NOT NULL,
    heart_rate INTEGER,
    systolic_bp INTEGER,
    diastolic_bp INTEGER,
    respiratory_rate INTEGER,
    temperature DECIMAL(4,1),
    spo2 INTEGER,
    news2_score INTEGER,
    qsofa_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_patient_timestamp (patient_id, timestamp)
);
```

#### Redis (Cache)
- **Purpose:** High-speed caching
- **Use Cases:**
  - Session storage
  - API response caching
  - Rate limiting counters
  - Real-time data
  - Pub/sub messaging

**Configuration:**
```
maxmemory 512mb
maxmemory-policy allkeys-lru
```

#### MinIO (Object Storage)
- **Purpose:** File & model storage
- **Buckets:**
  - medobsmind-models (AI models)
  - medobsmind-training (training data)
  - medobsmind-backups (database backups)
  - medobsmind-uploads (user uploads)

#### Vector Database (Chroma/FAISS)
- **Purpose:** RAG (Retrieval Augmented Generation)
- **Content:**
  - Medical guidelines (ICMR, AIIMS)
  - Drug formulary
  - Medical literature
  - Clinical protocols
- **Embedding:** sentence-transformers

### 6. Infrastructure Layer

#### Docker Containers
- **Services:**
  - nginx (reverse proxy)
  - backend (FastAPI)
  - postgres (database)
  - redis (cache)
  - minio (object storage)

**docker-compose.prod.yml:**
```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports: [80:80, 443:443]
    
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...
    
  postgres:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:alpine
    
  minio:
    image: minio/minio
    command: server /data
```

#### Monitoring & Logging
- **Metrics:** Prometheus
- **Visualization:** Grafana
- **Logs:** Loki + structured logging
- **Alerts:** Alertmanager
- **Tracing:** Jaeger (optional)

#### Backup Strategy
- **Database:** Daily automated backups (pg_dump)
- **Object Storage:** Replication to S3
- **Config:** Version controlled (Git)
- **Retention:** 30 days daily, 12 months monthly

## Data Flow

### Patient Monitoring Flow
```
1. Nurse enters vitals (Web/Mobile)
2. API receives & validates data
3. Vitals Service processes
4. Calculate NEWS2/qSOFA scores
5. Store in PostgreSQL
6. Check for alerts (AI Service)
7. Generate alerts if needed
8. Notify relevant users (WebSocket/Push)
9. Update dashboard (real-time)
```

### AI Inference Flow
```
1. User query received
2. Context retrieval (RAG from Vector DB)
3. Prompt engineering with context
4. LLM inference (dsquaremedicalmodel)
5. Safety guardrails check
6. Response formatting
7. Cache result (Redis)
8. Return to user
9. Log for training data
```

### Training Pipeline Flow
```
1. Collect data from multiple sources
2. Sanitize & anonymize
3. Store in training_data_pool
4. Quality filtering (score > 0.8)
5. Format for LoRA training
6. Train adapter (8 hours)
7. Merge with base model
8. Quantize to GGUF
9. Deploy automatically
10. Monitor performance
```

## Security Architecture

### Defense in Depth
1. **Network:** Firewall, DDoS protection
2. **Transport:** TLS 1.3, HTTPS only
3. **Application:** Input validation, CSRF, XSS
4. **Authentication:** OAuth 2.0, JWT, MFA
5. **Authorization:** RBAC, granular permissions
6. **Data:** Encryption at rest & in transit
7. **Audit:** Complete logging & monitoring

### Threat Modeling
- SQL Injection: ✅ Parameterized queries
- XSS: ✅ Input sanitization, CSP headers
- CSRF: ✅ CSRF tokens
- Session hijacking: ✅ Secure cookies, JWT
- Data breach: ✅ Encryption, access controls
- DDoS: ✅ Rate limiting, Cloudflare

## Scalability

### Horizontal Scaling
- **Backend:** Multiple FastAPI instances behind load balancer
- **Database:** Read replicas for queries
- **Cache:** Redis cluster
- **Storage:** MinIO distributed mode

### Vertical Scaling
- **CPU:** 8-16 cores recommended
- **RAM:** 16-32 GB for production
- **Disk:** SSD for database, NVMe for models

### Performance Targets
- API Response: < 200ms (p95)
- Page Load: < 2s
- LLM Inference: 2-3s
- Concurrent Users: 100-500
- Database Queries: < 50ms

## Deployment Options

### 1. Single Server (Small Hospital)
- All services on one machine
- Docker Compose
- 8 GB RAM, 4 cores, 50 GB disk
- Cost: ₹1,600/month

### 2. Multi-Server (Large Hospital)
- Separate servers for services
- Load balancer
- 32 GB RAM total, 16 cores
- Cost: ₹5,000/month

### 3. Cloud (Kubernetes)
- AWS EKS, GCP GKE, or Azure AKS
- Auto-scaling
- High availability
- Cost: ₹10,000+/month

### 4. Hybrid (Recommended)
- Critical services on-premise
- Static content on CDN
- Backup to cloud
- Cost: ₹3,000/month

## Disaster Recovery

### RPO (Recovery Point Objective): 0 hours
- Continuous replication
- Transaction logs
- No data loss

### RTO (Recovery Time Objective): 15 minutes
- Automated failover
- Hot standby
- Backup restoration

## Future Architecture

### Planned Enhancements
1. **Microservices:** Break into smaller services
2. **Event-Driven:** Apache Kafka for messaging
3. **Service Mesh:** Istio for service management
4. **Edge Computing:** Local inference at hospitals
5. **Blockchain:** Audit trail & consent management

---

## Technology Stack Summary

**Frontend:**
- React 18, TypeScript, Material-UI
- Android: Kotlin, Jetpack Compose
- iOS: SwiftUI

**Backend:**
- Python 3.11, FastAPI, Pydantic
- PostgreSQL 14, Redis
- MinIO, Chroma/FAISS

**AI/ML:**
- LLaMA-3 8B, llama.cpp
- PyTorch, ONNX Runtime
- Sentence Transformers

**Infrastructure:**
- Docker, Docker Compose
- Nginx, Let's Encrypt
- Prometheus, Grafana

**All Open Source, All Free!**

---

© 2026 d²media | MedObsMind.in
