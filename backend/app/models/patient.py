"""
Patient model - Core patient information.

FHIR-ready schema for patient demographics and medical history.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Date, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class GenderEnum(str, enum.Enum):
    """Gender options (FHIR-compliant)"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class Patient(Base):
    """
    Patient model - stores patient demographics and medical history.
    
    Attributes:
        id: Unique patient identifier (UUID)
        mrn: Medical Record Number (hospital-specific)
        first_name: Patient first name
        last_name: Patient last name
        date_of_birth: Patient date of birth
        gender: Patient gender
        contact_number: Phone number
        email: Email address
        address: Full address
        emergency_contact: Emergency contact details (JSON)
        allergies: Known allergies (JSON array)
        current_medications: Current medications (JSON array)
        medical_history: Past medical history (text)
        admission_date: Current admission date (if admitted)
        ward: Current ward/unit
        bed_number: Current bed number
        attending_doctor_id: ID of attending physician
        is_active: Patient active status
        metadata: Additional flexible data (JSONB)
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    """
    
    __tablename__ = "patients"
    
    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    mrn = Column(String(50), unique=True, nullable=False, index=True, comment="Medical Record Number")
    
    # Demographics
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(SQLEnum(GenderEnum), nullable=False)
    
    # Contact information
    contact_number = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    emergency_contact = Column(JSONB, comment="Emergency contact details")
    
    # Medical information
    allergies = Column(JSONB, default=list, comment="List of known allergies")
    current_medications = Column(JSONB, default=list, comment="Current medications")
    medical_history = Column(Text, comment="Past medical history")
    
    # Current admission info
    admission_date = Column(DateTime, nullable=True)
    ward = Column(String(50), comment="Current ward/unit")
    bed_number = Column(String(20), comment="Current bed number")
    attending_doctor_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Status
    is_active = Column(String(20), default="active", comment="Patient status: active, discharged, transferred")
    
    # Flexible metadata for hospital-specific fields
    metadata = Column(JSONB, default=dict, comment="Additional hospital-specific data")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    vitals = relationship("VitalsObservation", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(mrn={self.mrn}, name={self.first_name} {self.last_name})>"
    
    @property
    def full_name(self) -> str:
        """Get patient's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int:
        """Calculate patient's age"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
