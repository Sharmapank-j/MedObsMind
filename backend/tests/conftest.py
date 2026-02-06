# Test configuration and fixtures

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://medobsmind:testpassword@localhost:5432/medobsmind_test"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

# Create test session maker
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing"""
    return {
        "mrn": "TEST001",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-01",
        "gender": "male",
        "contact_number": "+91-9876543210",
        "email": "john.doe@example.com",
        "address": "123 Test Street, Mumbai, Maharashtra, 400001",
        "blood_group": "O+",
        "allergies": ["Penicillin"],
        "current_medications": ["Metformin 500mg BD"],
        "medical_history": "Type 2 Diabetes Mellitus",
        "admission_date": "2026-02-06",
        "ward": "ICU",
        "bed_number": "ICU-01",
        "attending_doctor": "Dr. Smith"
    }


@pytest.fixture
def sample_vitals_data():
    """Sample vitals data for testing"""
    return {
        "heart_rate": 75,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "spo2": 98,
        "respiratory_rate": 16,
        "temperature": 37.0,
        "consciousness_level": "A",
        "supplemental_oxygen": False,
        "notes": "Patient stable, routine monitoring",
        "data_source": "manual"
    }


@pytest.fixture
def sample_alert_data():
    """Sample alert data for testing"""
    return {
        "alert_type": "clinical_observation",
        "severity": "warning",
        "title": "Elevated heart rate",
        "message": "Heart rate above normal range",
        "clinical_context": {
            "vital_parameter": "heart_rate",
            "value": 110,
            "threshold": 100
        },
        "recommendations": [
            "Monitor patient closely",
            "Check for pain or anxiety",
            "Consider ECG if sustained"
        ]
    }
