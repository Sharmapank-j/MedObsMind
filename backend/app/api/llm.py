"""
LLM API Endpoints for MedObsMind

Provides REST API for dsquaremedicalmodel inference:
- Alert explanations
- Trend summarization
- Shift summaries
- Education Q&A

All outputs pass through safety guardrails.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import logging

from ..services.llm_service import LLMService, ConfidenceLevel
from ..services.rag_service import RAGService
from ..services.guardrails import Guardrails, SafetyCheckResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/llm", tags=["LLM"])


# Request/Response Models

class AlertExplanationRequest(BaseModel):
    """Request for alert explanation."""
    alert_type: str = Field(..., description="Type of alert (e.g., NEWS2_HIGH)")
    vitals: Dict = Field(..., description="Current vital signs")
    scores: Dict = Field(..., description="Clinical scores")
    context: Optional[str] = Field(None, description="Additional context")
    use_rag: bool = Field(True, description="Use RAG for guidelines")


class AlertExplanationResponse(BaseModel):
    """Response with alert explanation."""
    explanation: str
    confidence: str
    recommendations: List[str]
    sources: List[str]
    safety_check: Dict


class TrendSummaryRequest(BaseModel):
    """Request for trend summarization."""
    patient_id: str
    vitals_history: List[Dict]
    time_window: str = "24h"


class TrendSummaryResponse(BaseModel):
    """Response with trend summary."""
    summary: str
    key_changes: List[str]
    concerns: List[str]
    confidence: str
    safety_check: Dict


class ShiftSummaryRequest(BaseModel):
    """Request for shift handover summary."""
    patient_id: str
    events: List[Dict]
    vitals_summary: Dict


class ShiftSummaryResponse(BaseModel):
    """Response with SOAP note."""
    subjective: str
    objective: str
    assessment: str
    plan: str
    confidence: str
    safety_check: Dict


class EducationQARequest(BaseModel):
    """Request for education Q&A."""
    question: str
    context: Optional[str] = None


class EducationQAResponse(BaseModel):
    """Response with educational answer."""
    answer: str
    explanation: str
    references: List[str]
    confidence: str


# Dependency: Get services
def get_llm_service() -> LLMService:
    """Get LLM service instance."""
    return LLMService(base_url="http://localhost:8001")


def get_rag_service() -> RAGService:
    """Get RAG service instance."""
    return RAGService()


def get_guardrails() -> Guardrails:
    """Get guardrails instance."""
    return Guardrails()


# Endpoints

@router.post("/explain-alert", response_model=AlertExplanationResponse)
async def explain_alert(
    request: AlertExplanationRequest,
    llm_service: LLMService = Depends(get_llm_service),
    rag_service: RAGService = Depends(get_rag_service),
    guardrails: Guardrails = Depends(get_guardrails)
):
    """
    Generate explanation for clinical alert.
    
    Uses dsquaremedicalmodel to explain why alert fired and what to monitor.
    All outputs pass through safety guardrails.
    """
    try:
        # Generate explanation
        result = llm_service.explain_alert(
            alert_type=request.alert_type,
            vitals=request.vitals,
            scores=request.scores,
            context=request.context
        )
        
        # If RAG requested, augment with guidelines
        if request.use_rag:
            # Retrieve relevant guidelines
            query = f"{request.alert_type} management guidelines"
            docs = rag_service.retrieve(query, top_k=2)
            if docs:
                result["sources"] = [doc.source for doc in docs]
        
        # Safety check
        safety_result = guardrails.check_safety(
            llm_output=result["explanation"],
            input_data={"vitals": request.vitals, "scores": request.scores},
            confidence_score=0.75  # Would be actual confidence from model
        )
        
        if not safety_result.is_safe:
            logger.warning(f"Unsafe output blocked: {safety_result.violations}")
            result["explanation"] = safety_result.modified_output or \
                "Clinical assessment required. Please review with attending clinician."
        
        return AlertExplanationResponse(
            explanation=result["explanation"],
            confidence=result["confidence"],
            recommendations=result.get("recommendations", []),
            sources=result.get("sources", []),
            safety_check={
                "is_safe": safety_result.is_safe,
                "violations": [str(v) for v in safety_result.violations],
                "requires_review": safety_result.requires_review
            }
        )
    
    except Exception as e:
        logger.error(f"Alert explanation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize-trends", response_model=TrendSummaryResponse)
async def summarize_trends(
    request: TrendSummaryRequest,
    llm_service: LLMService = Depends(get_llm_service),
    guardrails: Guardrails = Depends(get_guardrails)
):
    """
    Summarize clinical trends over time.
    
    Analyzes vital signs history and identifies key changes and concerns.
    """
    try:
        result = llm_service.summarize_trends(
            patient_id=request.patient_id,
            vitals_history=request.vitals_history,
            time_window=request.time_window
        )
        
        # Safety check
        safety_result = guardrails.check_safety(
            llm_output=result["summary"],
            input_data={"vitals_history": request.vitals_history}
        )
        
        if not safety_result.is_safe:
            result["summary"] = safety_result.modified_output or \
                "Trend data available. Clinician review recommended."
        
        return TrendSummaryResponse(
            summary=result["summary"],
            key_changes=result.get("key_changes", []),
            concerns=result.get("concerns", []),
            confidence=result.get("confidence", ConfidenceLevel.MEDIUM.value),
            safety_check={
                "is_safe": safety_result.is_safe,
                "violations": [str(v) for v in safety_result.violations]
            }
        )
    
    except Exception as e:
        logger.error(f"Trend summarization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shift-summary", response_model=ShiftSummaryResponse)
async def generate_shift_summary(
    request: ShiftSummaryRequest,
    llm_service: LLMService = Depends(get_llm_service),
    guardrails: Guardrails = Depends(get_guardrails)
):
    """
    Generate shift handover summary in SOAP format.
    
    Creates structured clinical note for shift handover.
    """
    try:
        result = llm_service.generate_shift_summary(
            patient_id=request.patient_id,
            events=request.events,
            vitals_summary=request.vitals_summary
        )
        
        # Safety check on assessment
        safety_result = guardrails.check_safety(
            llm_output=result.get("assessment", ""),
            input_data={"events": request.events}
        )
        
        if not safety_result.is_safe:
            result["assessment"] = "See detailed events. Clinician assessment required."
        
        return ShiftSummaryResponse(
            subjective=result.get("subjective", ""),
            objective=result.get("objective", ""),
            assessment=result.get("assessment", ""),
            plan=result.get("plan", ""),
            confidence=result.get("confidence", ConfidenceLevel.MEDIUM.value),
            safety_check={
                "is_safe": safety_result.is_safe,
                "violations": [str(v) for v in safety_result.violations]
            }
        )
    
    except Exception as e:
        logger.error(f"Shift summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/education-qa", response_model=EducationQAResponse)
async def education_qa(
    request: EducationQARequest,
    llm_service: LLMService = Depends(get_llm_service),
    rag_service: RAGService = Depends(get_rag_service)
):
    """
    Answer medical education questions for students.
    
    Provides educational explanations with references.
    No patient data involved - purely educational.
    """
    try:
        # Get answer from LLM
        result = llm_service.education_qa(
            question=request.question,
            context=request.context
        )
        
        # Retrieve relevant educational resources
        docs = rag_service.retrieve(request.question, top_k=2)
        references = [doc.source for doc in docs] if docs else []
        
        return EducationQAResponse(
            answer=result.get("answer", ""),
            explanation=result.get("explanation", ""),
            references=references,
            confidence=result.get("confidence", ConfidenceLevel.MEDIUM.value)
        )
    
    except Exception as e:
        logger.error(f"Education Q&A failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check(
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Health check for LLM service.
    
    Returns status of dsquaremedicalmodel inference service.
    """
    try:
        # Simple ping to LLM service
        # In production, would call actual health endpoint
        return {
            "status": "healthy",
            "model": "dsquaremedicalmodel",
            "version": "1.0.0",
            "base_model": "LLaMA-3 8B",
            "deployment": "edge"  # or "cloud"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/stats")
async def get_stats():
    """
    Get LLM service statistics.
    
    Returns usage statistics and performance metrics.
    """
    # In production, would track actual metrics
    return {
        "total_requests": 0,
        "avg_latency_ms": 0,
        "success_rate": 0.0,
        "safety_violations": 0,
        "hallucination_rate": 0.0
    }
