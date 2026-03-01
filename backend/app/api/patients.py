"""
Patients API endpoints - Patient management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from app.core.database import get_db
from app.models.patient import Patient, GenderEnum
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

router = APIRouter()


# Pydantic schemas for request/response
class PatientCreate(BaseModel):
    """Schema for creating a new patient"""
    mrn: str = Field(..., description="Medical Record Number")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: GenderEnum
    contact_number: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    ward: str | None = None
    bed_number: str | None = None


class PatientResponse(BaseModel):
    """Schema for patient response"""
    id: UUID
    mrn: str
    first_name: str
    last_name: str
    full_name: str
    date_of_birth: date
    age: int
    gender: str
    contact_number: str | None
    ward: str | None
    bed_number: str | None
    is_active: str
    
    class Config:
        from_attributes = True


@router.post("/", response_model=PatientResponse, status_code=201)
async def create_patient(
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new patient in the system.
    
    - **mrn**: Medical Record Number (must be unique)
    - **first_name**: Patient's first name
    - **last_name**: Patient's last name
    - **date_of_birth**: Date of birth
    - **gender**: Gender (male/female/other/unknown)
    """
    # Check if MRN already exists
    result = await db.execute(
        select(Patient).where(Patient.mrn == patient_data.mrn)
    )
    existing_patient = result.scalar_one_or_none()
    
    if existing_patient:
        raise HTTPException(status_code=400, detail=f"Patient with MRN {patient_data.mrn} already exists")
    
    # Create new patient
    new_patient = Patient(**patient_data.model_dump())
    db.add(new_patient)
    await db.commit()
    await db.refresh(new_patient)
    
    return new_patient


@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    ward: str | None = None,
    is_active: str = "active",
    db: AsyncSession = Depends(get_db)
):
    """
    List all patients with optional filtering.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **ward**: Filter by ward
    - **is_active**: Filter by status (active/discharged/transferred)
    """
    query = select(Patient).where(Patient.is_active == is_active)
    
    if ward:
        query = query.where(Patient.ward == ward)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    patients = result.scalars().all()
    
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific patient.
    
    - **patient_id**: UUID of the patient
    """
    result = await db.execute(
        select(Patient).where(Patient.id == patient_id)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return patient


@router.get("/mrn/{mrn}", response_model=PatientResponse)
async def get_patient_by_mrn(
    mrn: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get patient by Medical Record Number.
    
    - **mrn**: Medical Record Number
    """
    result = await db.execute(
        select(Patient).where(Patient.mrn == mrn)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient with MRN {mrn} not found")
    
    return patient
