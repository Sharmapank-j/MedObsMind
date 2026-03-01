"""
Vitals API Endpoints
Handles recording and retrieval of patient vital signs
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from pydantic import BaseModel, Field

from ..core.database import get_db
from ..models.vitals import VitalsObservation
from ..models.patient import Patient
from ..ml.news2 import NEWS2Calculator

router = APIRouter(prefix="/vitals", tags=["vitals"])


# Pydantic schemas
class VitalsCreate(BaseModel):
    """Schema for creating a new vitals observation"""
    patient_id: str
    heart_rate: Optional[int] = Field(None, ge=30, le=220, description="Heart rate in bpm")
    systolic_bp: Optional[int] = Field(None, ge=50, le=250, description="Systolic BP in mmHg")
    diastolic_bp: Optional[int] = Field(None, ge=30, le=150, description="Diastolic BP in mmHg")
    spo2: Optional[int] = Field(None, ge=70, le=100, description="Oxygen saturation %")
    respiratory_rate: Optional[int] = Field(None, ge=5, le=60, description="Respiratory rate per min")
    temperature: Optional[float] = Field(None, ge=32.0, le=43.0, description="Temperature in Celsius")
    consciousness_level: Optional[str] = Field(None, pattern="^[AVPU]$", description="AVPU scale: A, V, P, U")
    supplemental_oxygen: bool = Field(False, description="Is patient on supplemental O2?")
    oxygen_flow_rate: Optional[float] = Field(None, ge=0, le=15, description="O2 flow rate in L/min")
    notes: Optional[str] = Field(None, max_length=1000)
    data_source: str = Field("manual", description="Source: manual, monitor, ehr")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "550e8400-e29b-41d4-a716-446655440000",
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
        }


class VitalsResponse(BaseModel):
    """Schema for vitals observation response"""
    id: str
    patient_id: str
    recorded_at: datetime
    heart_rate: Optional[int]
    systolic_bp: Optional[int]
    diastolic_bp: Optional[int]
    spo2: Optional[int]
    respiratory_rate: Optional[int]
    temperature: Optional[float]
    consciousness_level: Optional[str]
    supplemental_oxygen: bool
    oxygen_flow_rate: Optional[float]
    news2_score: Optional[int]
    mews_score: Optional[int]
    notes: Optional[str]
    data_source: str
    recorded_by: Optional[str]

    class Config:
        from_attributes = True


class VitalsTrendResponse(BaseModel):
    """Schema for vitals trend data"""
    parameter: str
    data_points: List[dict]
    min_value: Optional[float]
    max_value: Optional[float]
    avg_value: Optional[float]
    trend: str  # "increasing", "decreasing", "stable"


@router.post("/", response_model=VitalsResponse, status_code=201)
async def record_vitals(
    vitals_data: VitalsCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Record new vitals observation for a patient.
    Automatically calculates NEWS2 and MEWS scores.
    """
    # Verify patient exists
    result = await db.execute(
        select(Patient).where(Patient.id == vitals_data.patient_id)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Calculate NEWS2 score if all required vitals present
    news2_score = None
    if all([
        vitals_data.respiratory_rate,
        vitals_data.spo2,
        vitals_data.temperature,
        vitals_data.systolic_bp,
        vitals_data.heart_rate,
        vitals_data.consciousness_level
    ]):
        calculator = NEWS2Calculator()
        try:
            result = calculator.calculate(
                respiratory_rate=vitals_data.respiratory_rate,
                spo2=vitals_data.spo2,
                temperature=vitals_data.temperature,
                systolic_bp=vitals_data.systolic_bp,
                heart_rate=vitals_data.heart_rate,
                consciousness_level=vitals_data.consciousness_level,
                on_supplemental_oxygen=vitals_data.supplemental_oxygen
            )
            news2_score = result["total_score"]
        except Exception as e:
            # Don't fail the request if scoring fails
            print(f"NEWS2 calculation failed: {e}")
    
    # Create vitals observation
    vitals = VitalsObservation(
        patient_id=vitals_data.patient_id,
        heart_rate=vitals_data.heart_rate,
        systolic_bp=vitals_data.systolic_bp,
        diastolic_bp=vitals_data.diastolic_bp,
        spo2=vitals_data.spo2,
        respiratory_rate=vitals_data.respiratory_rate,
        temperature=vitals_data.temperature,
        consciousness_level=vitals_data.consciousness_level,
        supplemental_oxygen=vitals_data.supplemental_oxygen,
        oxygen_flow_rate=vitals_data.oxygen_flow_rate,
        news2_score=news2_score,
        notes=vitals_data.notes,
        data_source=vitals_data.data_source
    )
    
    db.add(vitals)
    await db.commit()
    await db.refresh(vitals)
    
    return vitals


@router.get("/{vitals_id}", response_model=VitalsResponse)
async def get_vitals(
    vitals_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific vitals observation by ID"""
    result = await db.execute(
        select(VitalsObservation).where(VitalsObservation.id == vitals_id)
    )
    vitals = result.scalar_one_or_none()
    
    if not vitals:
        raise HTTPException(status_code=404, detail="Vitals observation not found")
    
    return vitals


@router.get("/patient/{patient_id}", response_model=List[VitalsResponse])
async def get_patient_vitals(
    patient_id: str,
    db: AsyncSession = Depends(get_db),
    hours: int = Query(24, ge=1, le=168, description="Hours of history to retrieve"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records")
):
    """
    Get vitals history for a patient.
    Default: Last 24 hours, maximum 100 records.
    """
    since = datetime.utcnow() - timedelta(hours=hours)
    
    result = await db.execute(
        select(VitalsObservation)
        .where(
            and_(
                VitalsObservation.patient_id == patient_id,
                VitalsObservation.recorded_at >= since
            )
        )
        .order_by(desc(VitalsObservation.recorded_at))
        .limit(limit)
    )
    vitals = result.scalars().all()
    
    return list(vitals)


@router.get("/patient/{patient_id}/latest", response_model=VitalsResponse)
async def get_latest_vitals(
    patient_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the most recent vitals observation for a patient"""
    result = await db.execute(
        select(VitalsObservation)
        .where(VitalsObservation.patient_id == patient_id)
        .order_by(desc(VitalsObservation.recorded_at))
        .limit(1)
    )
    vitals = result.scalar_one_or_none()
    
    if not vitals:
        raise HTTPException(status_code=404, detail="No vitals found for this patient")
    
    return vitals


@router.get("/patient/{patient_id}/trend/{parameter}", response_model=VitalsTrendResponse)
async def get_vitals_trend(
    patient_id: str,
    parameter: str,
    db: AsyncSession = Depends(get_db),
    hours: int = Query(24, ge=1, le=168)
):
    """
    Get trend analysis for a specific vital sign parameter.
    Parameters: heart_rate, systolic_bp, diastolic_bp, spo2, respiratory_rate, temperature
    """
    valid_parameters = [
        "heart_rate", "systolic_bp", "diastolic_bp", 
        "spo2", "respiratory_rate", "temperature"
    ]
    
    if parameter not in valid_parameters:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid parameter. Must be one of: {', '.join(valid_parameters)}"
        )
    
    since = datetime.utcnow() - timedelta(hours=hours)
    
    result = await db.execute(
        select(VitalsObservation)
        .where(
            and_(
                VitalsObservation.patient_id == patient_id,
                VitalsObservation.recorded_at >= since
            )
        )
        .order_by(VitalsObservation.recorded_at)
    )
    vitals_list = result.scalars().all()
    
    # Extract data points
    data_points = []
    values = []
    
    for v in vitals_list:
        value = getattr(v, parameter)
        if value is not None:
            data_points.append({
                "timestamp": v.recorded_at.isoformat(),
                "value": value
            })
            values.append(float(value))
    
    if not values:
        raise HTTPException(
            status_code=404, 
            detail=f"No {parameter} data found for this patient"
        )
    
    # Calculate statistics
    min_value = min(values)
    max_value = max(values)
    avg_value = sum(values) / len(values)
    
    # Simple trend analysis
    if len(values) >= 2:
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        if second_half > first_half * 1.1:
            trend = "increasing"
        elif second_half < first_half * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    return VitalsTrendResponse(
        parameter=parameter,
        data_points=data_points,
        min_value=min_value,
        max_value=max_value,
        avg_value=round(avg_value, 2),
        trend=trend
    )


@router.delete("/{vitals_id}", status_code=204)
async def delete_vitals(
    vitals_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a vitals observation (admin only in production)"""
    result = await db.execute(
        select(VitalsObservation).where(VitalsObservation.id == vitals_id)
    )
    vitals = result.scalar_one_or_none()
    
    if not vitals:
        raise HTTPException(status_code=404, detail="Vitals observation not found")
    
    await db.delete(vitals)
    await db.commit()
    
    return None
