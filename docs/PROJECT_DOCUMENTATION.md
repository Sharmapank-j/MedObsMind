# MedObsMind - Project Documentation

## Complete Medical Observation & Clinical Decision Support System

### Architecture Overview

```
Android App → FastAPI Backend → PostgreSQL Database
                    ↓
                  Redis
                    ↓
            NEWS2/MEWS/ML Engine
```

### Core Components

**Backend (FastAPI)**
- Patient management API
- Vitals recording and monitoring
- Alert generation and management
- NEWS2 scoring engine
- Real-time notifications

**Database (PostgreSQL)**
- Patients table (demographics, admission info)
- Vitals observations (time-series vital signs)
- Alerts (clinical alerts and notifications)
- Audit logs

**Mobile (Android)**
- Vitals entry interface
- Real-time patient monitoring
- Alert dashboard
- Offline-first functionality

### Medical Algorithms

**NEWS2 (National Early Warning Score 2)**
- 7 parameters scored (RR, SpO₂, O₂, Temp, SBP, HR, Consciousness)
- Risk levels: Low (0-4), Medium (5-6), High (7+)
- Automated clinical recommendations
- Validated against RCP guidelines

### API Endpoints

```
POST /api/v1/patients - Create patient
GET  /api/v1/patients - List patients
GET  /api/v1/patients/{id} - Get patient
POST /api/v1/vitals - Record vitals
GET  /api/v1/vitals/{patient_id}/trend - Get trends
GET  /api/v1/alerts - List active alerts
```

### Deployment

**Docker Compose**:
```bash
docker-compose up -d
```

**Manual Setup**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Security

- Doctor-in-loop required
- Complete audit logging
- HIPAA-ready architecture
- No autonomous decisions

For complete documentation, see individual files in `/docs` directory.
