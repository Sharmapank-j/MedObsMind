# MedObsMind Backend

AI-powered medical observation and clinical decision support system backend.

## Tech Stack

- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Primary database
- **Redis**: Alert queuing and caching
- **SQLAlchemy**: ORM
- **Alembic**: Database migrations

## Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Redis 6+

### Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost/medobsmind
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
```

### Database Setup

```bash
# Run migrations
alembic upgrade head

# Create initial data (optional)
python -m app.core.init_db
```

### Running the Server

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/                 # API endpoints
│   │   ├── patients.py     # Patient management
│   │   ├── vitals.py       # Vitals recording
│   │   ├── alerts.py       # Alert management
│   │   └── auth.py         # Authentication
│   ├── models/              # Database models
│   │   ├── patient.py
│   │   ├── vitals.py
│   │   ├── alert.py
│   │   └── user.py
│   ├── services/            # Business logic
│   │   ├── alert_engine.py # Alert generation
│   │   ├── risk_scoring.py # Risk calculation
│   │   └── notifications.py
│   ├── ml/                  # ML models
│   │   ├── news2.py        # NEWS2 scoring
│   │   ├── mews.py         # MEWS scoring
│   │   └── predictor.py    # ML predictions
│   ├── core/                # Core configuration
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   └── main.py              # FastAPI app
├── tests/                   # Unit tests
├── alembic/                 # Database migrations
├── requirements.txt
└── README.md
```

## Key Features

### 1. Patient Management
- Patient registration
- Medical history
- Current medications
- Allergies

### 2. Vitals Monitoring
- Real-time vitals entry (HR, BP, SpO₂, RR, Temp)
- Automated trend analysis
- Time-series visualization
- Threshold alerts

### 3. Alert System
- NEWS2 scoring (National Early Warning Score)
- MEWS scoring (Modified Early Warning Score)
- Rule-based alerts
- Escalation protocols
- Doctor notifications

### 4. Risk Prediction
- Sepsis risk
- Shock prediction
- Cardiac arrest risk
- ICU deterioration

### 5. Clinical Decision Support
- Lab-vitals correlation
- Treatment suggestions
- Drug interaction warnings
- Evidence-based protocols

## Security

- JWT authentication
- Role-based access control (RBAC)
- Audit logging for all actions
- HIPAA-ready data handling
- Doctor-in-loop always

## Medical Safety

⚠️ **Important**: This system is for clinical decision SUPPORT only.
- No autonomous medical decisions
- All alerts require doctor review
- Suggestions are advisory, not prescriptive
- Complete audit trail maintained

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_vitals.py
```

## Deployment

See [DEPLOYMENT.md](../docs/DEPLOYMENT.md) for production deployment guide.

## License

© 2026 MedObsMind. All rights reserved.
