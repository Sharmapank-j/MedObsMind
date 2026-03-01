"""
Vitals observation model - Real-time patient vital signs monitoring.

Supports both manual entry and device integration.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class VitalsObservation(Base):
    """
    Vitals observation model - stores patient vital signs readings.
    
    Core vital signs tracked:
    - Heart Rate (HR) - beats per minute
    - Blood Pressure (BP) - systolic/diastolic mmHg
    - Oxygen Saturation (SpO₂) - percentage
    - Respiratory Rate (RR) - breaths per minute
    - Temperature (Temp) - Celsius
    - Consciousness Level (AVPU scale)
    
    Attributes:
        id: Unique observation ID
        patient_id: Reference to patient
        observed_at: Timestamp of observation
        recorded_by: ID of staff who recorded (for audit)
        
        # Core vitals
        heart_rate: Heart rate (bpm)
        systolic_bp: Systolic blood pressure (mmHg)
        diastolic_bp: Diastolic blood pressure (mmHg)
        spo2: Oxygen saturation (%)
        respiratory_rate: Breaths per minute
        temperature: Body temperature (°C)
        consciousness_level: AVPU (Alert, Voice, Pain, Unresponsive)
        
        # Additional clinical data
        supplemental_oxygen: Whether patient is on O2
        oxygen_flow_rate: O2 flow rate (L/min)
        
        # Scores calculated at time of observation
        news2_score: NEWS2 score calculated
        mews_score: MEWS score calculated
        
        # Metadata
        source: manual, device, ehr_import
        device_id: Device identifier if from device
        notes: Clinical notes
        is_valid: Data validation flag
    """
    
    __tablename__ = "vitals_observations"
    
    # Primary key and foreign keys
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    
    # Observation metadata
    observed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    recorded_by = Column(UUID(as_uuid=True), comment="Staff member who recorded")
    
    # Core vital signs
    heart_rate = Column(Float, comment="Heart rate (bpm)")
    systolic_bp = Column(Float, comment="Systolic BP (mmHg)")
    diastolic_bp = Column(Float, comment="Diastolic BP (mmHg)")
    spo2 = Column(Float, comment="Oxygen saturation (%)")
    respiratory_rate = Column(Float, comment="Respiratory rate (breaths/min)")
    temperature = Column(Float, comment="Temperature (°C)")
    consciousness_level = Column(String(20), comment="AVPU: Alert, Voice, Pain, Unresponsive")
    
    # Oxygen therapy
    supplemental_oxygen = Column(Boolean, default=False, comment="Patient on supplemental O2")
    oxygen_flow_rate = Column(Float, comment="O2 flow rate (L/min)")
    
    # Calculated scores (stored for historical tracking)
    news2_score = Column(Float, comment="NEWS2 score at time of observation")
    mews_score = Column(Float, comment="MEWS score at time of observation")
    
    # Additional data
    source = Column(String(20), default="manual", comment="Data source: manual, device, ehr_import")
    device_id = Column(String(100), comment="Device identifier if automated")
    notes = Column(Text, comment="Clinical notes from observer")
    is_valid = Column(Boolean, default=True, comment="Data validation flag")
    
    # Flexible metadata
    extra_metadata = Column('metadata', JSONB, default=dict, comment="Additional vitals or device data")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    patient = relationship("Patient", back_populates="vitals")
    
    def __repr__(self):
        return f"<VitalsObservation(patient_id={self.patient_id}, observed_at={self.observed_at})>"
    
    @property
    def is_complete(self) -> bool:
        """Check if observation has all core vitals"""
        required_vitals = [
            self.heart_rate,
            self.systolic_bp,
            self.diastolic_bp,
            self.spo2,
            self.respiratory_rate,
            self.temperature,
            self.consciousness_level
        ]
        return all(v is not None for v in required_vitals)
    
    @property
    def blood_pressure(self) -> str:
        """Format blood pressure as string"""
        if self.systolic_bp and self.diastolic_bp:
            return f"{int(self.systolic_bp)}/{int(self.diastolic_bp)}"
        return "N/A"
