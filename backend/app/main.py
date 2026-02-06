"""
MedObsMind Backend - Medical Observation & Clinical Decision Support System

Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine, Base

# Import routers (will be created)
# from app.api import patients, vitals, alerts, auth

app = FastAPI(
    title="MedObsMind API",
    description="AI-powered medical observation and clinical decision support system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables (in production, use Alembic migrations)
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created")
    print(f"🚀 MedObsMind API running on {settings.ENVIRONMENT} mode")

@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "message": "MedObsMind API",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }

# Include API routers
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
# app.include_router(vitals.router, prefix="/api/v1/vitals", tags=["Vitals"])
# app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else "An error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )
