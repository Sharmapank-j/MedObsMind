"""
Alerts API Endpoints
Handles clinical alert management and notifications
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, or_
from pydantic import BaseModel, Field
from enum import Enum

from ..core.database import get_db
from ..models.alert import Alert, AlertType, AlertSeverity, AlertStatus
from ..models.patient import Patient

router = APIRouter(prefix="/alerts", tags=["alerts"])


# Pydantic schemas
class AlertResponse(BaseModel):
    """Schema for alert response"""
    id: str
    patient_id: str
    alert_type: str
    severity: str
    title: str
    message: str
    clinical_context: Optional[dict]
    news2_score: Optional[int]
    mews_score: Optional[int]
    recommendations: Optional[List[str]]
    status: str
    triggered_at: datetime
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[str]
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    resolution_notes: Optional[str]
    escalated: bool
    escalated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AlertCreate(BaseModel):
    """Schema for creating a manual alert"""
    patient_id: str
    alert_type: str
    severity: str
    title: str
    message: str
    clinical_context: Optional[dict] = None
    news2_score: Optional[int] = None
    recommendations: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "550e8400-e29b-41d4-a716-446655440000",
                "alert_type": "clinical_observation",
                "severity": "warning",
                "title": "Patient appears distressed",
                "message": "Patient reporting chest discomfort, requires evaluation",
                "clinical_context": {
                    "reporter": "Nurse Station 3",
                    "observation": "Patient clutching chest"
                },
                "recommendations": ["Immediate clinical assessment", "ECG if not done recently"]
            }
        }


class AlertAcknowledge(BaseModel):
    """Schema for acknowledging an alert"""
    acknowledged_by: str
    notes: Optional[str] = None


class AlertResolve(BaseModel):
    """Schema for resolving an alert"""
    resolved_by: str
    resolution_notes: str
    outcome: Optional[str] = None  # "true_positive", "false_positive", "clinical_intervention", "self_resolved"


class AlertEscalate(BaseModel):
    """Schema for escalating an alert"""
    escalated_by: str
    escalation_reason: str
    escalated_to: str  # Team or person


class AlertStats(BaseModel):
    """Alert statistics"""
    total_alerts: int
    active_alerts: int
    acknowledged_alerts: int
    resolved_alerts: int
    critical_alerts: int
    high_alerts: int
    medium_alerts: int
    low_alerts: int
    avg_response_time_minutes: Optional[float]


@router.post("/", response_model=AlertResponse, status_code=201)
async def create_alert(
    alert_data: AlertCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new alert (manual entry by clinician).
    Automatic alerts are created by the alert engine service.
    """
    # Verify patient exists
    result = await db.execute(
        select(Patient).where(Patient.id == alert_data.patient_id)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Validate alert type and severity
    try:
        alert_type = AlertType[alert_data.alert_type.upper()]
        severity = AlertSeverity[alert_data.severity.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid alert_type or severity. Valid types: {[e.name for e in AlertType]}, Valid severities: {[e.name for e in AlertSeverity]}"
        )
    
    # Create alert
    alert = Alert(
        patient_id=alert_data.patient_id,
        alert_type=alert_type,
        severity=severity,
        title=alert_data.title,
        message=alert_data.message,
        clinical_context=alert_data.clinical_context or {},
        news2_score=alert_data.news2_score,
        recommendations=alert_data.recommendations or []
    )
    
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    return alert


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    db: AsyncSession = Depends(get_db),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    status: Optional[str] = Query(None, description="Filter by status"),
    hours: int = Query(24, ge=1, le=168, description="Hours of history"),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Get alerts with optional filters.
    Default: All alerts from last 24 hours.
    """
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Build query
    conditions = [Alert.triggered_at >= since]
    
    if patient_id:
        conditions.append(Alert.patient_id == patient_id)
    
    if severity:
        try:
            sev = AlertSeverity[severity.upper()]
            conditions.append(Alert.severity == sev)
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
    
    if status:
        try:
            stat = AlertStatus[status.upper()]
            conditions.append(Alert.status == stat)
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    result = await db.execute(
        select(Alert)
        .where(and_(*conditions))
        .order_by(desc(Alert.triggered_at))
        .limit(limit)
    )
    alerts = result.scalars().all()
    
    return list(alerts)


@router.get("/active", response_model=List[AlertResponse])
async def get_active_alerts(
    db: AsyncSession = Depends(get_db),
    patient_id: Optional[str] = Query(None)
):
    """
    Get all active (unresolved) alerts.
    Useful for ICU dashboard and notification panels.
    """
    conditions = [Alert.status == AlertStatus.ACTIVE]
    
    if patient_id:
        conditions.append(Alert.patient_id == patient_id)
    
    result = await db.execute(
        select(Alert)
        .where(and_(*conditions))
        .order_by(desc(Alert.severity), desc(Alert.triggered_at))
    )
    alerts = result.scalars().all()
    
    return list(alerts)


@router.get("/critical", response_model=List[AlertResponse])
async def get_critical_alerts(
    db: AsyncSession = Depends(get_db),
    hours: int = Query(1, ge=1, le=24)
):
    """
    Get all critical alerts from the last N hours.
    Critical alerts require immediate attention.
    """
    since = datetime.utcnow() - timedelta(hours=hours)
    
    result = await db.execute(
        select(Alert)
        .where(
            and_(
                Alert.severity == AlertSeverity.CRITICAL,
                Alert.triggered_at >= since
            )
        )
        .order_by(desc(Alert.triggered_at))
    )
    alerts = result.scalars().all()
    
    return list(alerts)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific alert by ID"""
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return alert


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: str,
    ack_data: AlertAcknowledge,
    db: AsyncSession = Depends(get_db)
):
    """
    Acknowledge an alert.
    This indicates a clinician has seen the alert.
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.status == AlertStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="Cannot acknowledge a resolved alert")
    
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = ack_data.acknowledged_by
    
    if ack_data.notes:
        if not alert.clinical_context:
            alert.clinical_context = {}
        alert.clinical_context["acknowledgment_notes"] = ack_data.notes
    
    await db.commit()
    await db.refresh(alert)
    
    return alert


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: str,
    resolve_data: AlertResolve,
    db: AsyncSession = Depends(get_db)
):
    """
    Resolve an alert.
    This closes the alert and records the outcome.
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.status == AlertStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="Alert is already resolved")
    
    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = resolve_data.resolved_by
    alert.resolution_notes = resolve_data.resolution_notes
    
    if resolve_data.outcome:
        if not alert.clinical_context:
            alert.clinical_context = {}
        alert.clinical_context["resolution_outcome"] = resolve_data.outcome
    
    await db.commit()
    await db.refresh(alert)
    
    return alert


@router.post("/{alert_id}/escalate", response_model=AlertResponse)
async def escalate_alert(
    alert_id: str,
    escalate_data: AlertEscalate,
    db: AsyncSession = Depends(get_db)
):
    """
    Escalate an alert to a higher level of care or different team.
    """
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.status == AlertStatus.RESOLVED:
        raise HTTPException(status_code=400, detail="Cannot escalate a resolved alert")
    
    alert.escalated = True
    alert.escalated_at = datetime.utcnow()
    
    if not alert.clinical_context:
        alert.clinical_context = {}
    
    alert.clinical_context["escalation"] = {
        "escalated_by": escalate_data.escalated_by,
        "escalated_to": escalate_data.escalated_to,
        "reason": escalate_data.escalation_reason,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await db.commit()
    await db.refresh(alert)
    
    return alert


@router.get("/stats/summary", response_model=AlertStats)
async def get_alert_stats(
    db: AsyncSession = Depends(get_db),
    hours: int = Query(24, ge=1, le=168)
):
    """
    Get alert statistics for the specified time period.
    Useful for dashboards and monitoring.
    """
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Get all alerts in time period
    result = await db.execute(
        select(Alert).where(Alert.triggered_at >= since)
    )
    all_alerts = result.scalars().all()
    
    total_alerts = len(all_alerts)
    active_alerts = sum(1 for a in all_alerts if a.status == AlertStatus.ACTIVE)
    acknowledged_alerts = sum(1 for a in all_alerts if a.status == AlertStatus.ACKNOWLEDGED)
    resolved_alerts = sum(1 for a in all_alerts if a.status == AlertStatus.RESOLVED)
    
    critical_alerts = sum(1 for a in all_alerts if a.severity == AlertSeverity.CRITICAL)
    high_alerts = sum(1 for a in all_alerts if a.severity == AlertSeverity.HIGH)
    medium_alerts = sum(1 for a in all_alerts if a.severity == AlertSeverity.MEDIUM)
    low_alerts = sum(1 for a in all_alerts if a.severity == AlertSeverity.LOW)
    
    # Calculate average response time (time to acknowledgment)
    response_times = []
    for alert in all_alerts:
        if alert.acknowledged_at:
            response_time = (alert.acknowledged_at - alert.triggered_at).total_seconds() / 60
            response_times.append(response_time)
    
    avg_response_time = sum(response_times) / len(response_times) if response_times else None
    
    return AlertStats(
        total_alerts=total_alerts,
        active_alerts=active_alerts,
        acknowledged_alerts=acknowledged_alerts,
        resolved_alerts=resolved_alerts,
        critical_alerts=critical_alerts,
        high_alerts=high_alerts,
        medium_alerts=medium_alerts,
        low_alerts=low_alerts,
        avg_response_time_minutes=round(avg_response_time, 2) if avg_response_time else None
    )


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete an alert (admin only, for data cleanup)"""
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    await db.delete(alert)
    await db.commit()
    
    return None
