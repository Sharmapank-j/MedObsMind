"""
Feedback Collection Service for MedObsMind

Collects clinical feedback, model performance data, and alert outcomes
for continuous model improvement while maintaining offline-first operation.

Author: MedObsMind Team
License: MIT
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class FeedbackType(str, Enum):
    """Types of feedback that can be collected"""
    CLINICAL_CORRECTION = "clinical_correction"
    ALERT_OUTCOME = "alert_outcome"
    MODEL_PERFORMANCE = "model_performance"
    USER_EXPERIENCE = "user_experience"
    ERROR_REPORT = "error_report"


class FeedbackPriority(int, Enum):
    """Priority levels for feedback upload"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BATCH = 5


class FeedbackService:
    """
    Service for collecting and managing clinical feedback.
    
    Features:
    - Automatic feedback collection
    - Context capture (vitals, scores, clinical notes)
    - Rating system (1-5 stars)
    - Offline-first storage
    - Upload queue management
    """
    
    def __init__(self, db_session):
        self.db = db_session
        self.feedback_queue = []
        
    async def collect_feedback(
        self,
        feedback_type: FeedbackType,
        context: Dict[str, Any],
        rating: Optional[int] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None,
        patient_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Collect feedback from clinician.
        
        Args:
            feedback_type: Type of feedback
            context: Clinical context (vitals, alerts, suggestions)
            rating: Optional rating (1-5)
            notes: Optional free-text notes
            user_id: Doctor/nurse submitting feedback
            patient_id: Patient ID (will be hashed during sanitization)
            
        Returns:
            Feedback record with ID and status
        """
        try:
            # Generate unique feedback ID
            feedback_id = self._generate_feedback_id()
            
            # Determine priority based on type
            priority = self._get_priority(feedback_type, rating)
            
            # Create feedback record
            feedback = {
                "feedback_id": feedback_id,
                "type": feedback_type.value,
                "context": context,
                "rating": rating,
                "notes": notes,
                "user_id": user_id,
                "patient_id": patient_id,
                "priority": priority,
                "created_at": datetime.utcnow().isoformat(),
                "sanitized": False,
                "uploaded": False,
                "attempts": 0
            }
            
            # Store locally first (offline-first)
            await self._store_feedback(feedback)
            
            logger.info(f"Feedback collected: {feedback_id} (type: {feedback_type.value})")
            
            return {
                "feedback_id": feedback_id,
                "status": "collected",
                "sanitization_status": "pending",
                "upload_status": "queued",
                "priority": priority
            }
            
        except Exception as e:
            logger.error(f"Error collecting feedback: {str(e)}")
            raise
            
    def _generate_feedback_id(self) -> str:
        """Generate unique feedback ID"""
        from uuid import uuid4
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        unique_id = str(uuid4())[:8]
        return f"FB-{timestamp}-{unique_id}"
        
    def _get_priority(self, feedback_type: FeedbackType, rating: Optional[int]) -> int:
        """Determine upload priority based on feedback type and rating"""
        if feedback_type == FeedbackType.ERROR_REPORT:
            return FeedbackPriority.CRITICAL
        elif feedback_type == FeedbackType.CLINICAL_CORRECTION:
            return FeedbackPriority.HIGH
        elif feedback_type == FeedbackType.ALERT_OUTCOME:
            if rating and rating <= 2:  # Poor outcome
                return FeedbackPriority.HIGH
            return FeedbackPriority.MEDIUM
        elif feedback_type == FeedbackType.MODEL_PERFORMANCE:
            return FeedbackPriority.MEDIUM
        else:
            return FeedbackPriority.LOW
            
    async def _store_feedback(self, feedback: Dict[str, Any]):
        """Store feedback in local database"""
        # In production, this would use SQLAlchemy with the Feedback model
        # For now, we'll use a simple queue
        self.feedback_queue.append(feedback)
        
    async def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback collection statistics"""
        stats = {
            "collected": {
                "total": len(self.feedback_queue),
                "today": 0,
                "this_week": 0
            },
            "sanitized": {
                "total": 0,
                "pending": len([f for f in self.feedback_queue if not f["sanitized"]]),
                "failed": 0
            },
            "uploaded": {
                "total": 0,
                "pending": len([f for f in self.feedback_queue if not f["uploaded"]]),
                "failed": 0
            }
        }
        return stats
        
    async def get_pending_feedbacks(
        self,
        feedback_type: Optional[FeedbackType] = None,
        priority: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get pending feedbacks for processing"""
        pending = [f for f in self.feedback_queue if not f["uploaded"]]
        
        if feedback_type:
            pending = [f for f in pending if f["type"] == feedback_type.value]
            
        if priority:
            pending = [f for f in pending if f["priority"] == priority]
            
        # Sort by priority and creation time
        pending.sort(key=lambda x: (x["priority"], x["created_at"]))
        
        return pending
        
    async def mark_feedback_processed(
        self,
        feedback_id: str,
        sanitized: bool = False,
        uploaded: bool = False
    ):
        """Mark feedback as sanitized/uploaded"""
        for feedback in self.feedback_queue:
            if feedback["feedback_id"] == feedback_id:
                if sanitized:
                    feedback["sanitized"] = True
                    feedback["sanitized_at"] = datetime.utcnow().isoformat()
                if uploaded:
                    feedback["uploaded"] = True
                    feedback["uploaded_at"] = datetime.utcnow().isoformat()
                break
