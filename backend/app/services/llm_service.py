"""
LLM Service for MedObsMind - Interface to dsquaremedicalmodel

This service provides:
- Alert explanation generation
- Clinical trend summarization
- Shift handover generation
- Education mode Q&A

Model: dsquaremedicalmodel (d²media Medical AI Model)
Based on: LLaMA-3 8B fine-tuned with LoRA on Indian medical data
"""

import logging
from typing import Dict, List, Optional
import requests
from enum import Enum

logger = logging.getLogger(__name__)


class ConfidenceLevel(str, Enum):
    """Confidence level for LLM outputs."""
    HIGH = "high"  # >85% confidence
    MEDIUM = "medium"  # 60-85% confidence
    LOW = "low"  # <60% confidence


class LLMService:
    """
    Interface to dsquaremedicalmodel inference service.
    
    Supports both edge (CPU) and cloud (GPU) deployments.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        temperature: float = 0.3,
        max_tokens: int = 512,
        timeout: int = 30
    ):
        """
        Initialize LLM service.
        
        Args:
            base_url: URL of llama.cpp server or inference endpoint
            temperature: Sampling temperature (0.1-1.0, lower = more focused)
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        # Verify connection
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            logger.info(f"LLM service connected: {response.json()}")
        except Exception as e:
            logger.warning(f"LLM service not available: {e}")
    
    def explain_alert(
        self,
        alert_type: str,
        vitals: Dict,
        scores: Dict,
        context: Optional[str] = None
    ) -> Dict:
        """
        Generate explanation for clinical alert.
        
        Args:
            alert_type: Type of alert (e.g., "NEWS2_HIGH", "SEPSIS_RISK")
            vitals: Dictionary of vital signs
            scores: Dictionary of clinical scores (NEWS2, qSOFA, etc.)
            context: Optional additional context
        
        Returns:
            {
                "explanation": str,
                "confidence": str,
                "recommendations": List[str],
                "sources": List[str]
            }
        """
        prompt = self._create_alert_prompt(alert_type, vitals, scores, context)
        
        try:
            response = self._generate(prompt)
            explanation = self._parse_alert_response(response)
            
            return {
                "explanation": explanation["text"],
                "confidence": self._calculate_confidence(response),
                "recommendations": explanation.get("recommendations", []),
                "sources": explanation.get("sources", [])
            }
        except Exception as e:
            logger.error(f"Alert explanation failed: {e}")
            return self._fallback_alert_explanation(alert_type, scores)
    
    def summarize_trends(
        self,
        patient_id: str,
        vitals_history: List[Dict],
        time_window: str = "24h"
    ) -> Dict:
        """
        Summarize clinical trends over time.
        
        Args:
            patient_id: Patient identifier
            vitals_history: List of vital sign measurements
            time_window: Time window for analysis
        
        Returns:
            {
                "summary": str,
                "key_changes": List[str],
                "concerns": List[str],
                "confidence": str
            }
        """
        prompt = self._create_trend_prompt(vitals_history, time_window)
        
        try:
            response = self._generate(prompt)
            return self._parse_trend_response(response)
        except Exception as e:
            logger.error(f"Trend summarization failed: {e}")
            return self._fallback_trend_summary(vitals_history)
    
    def generate_shift_summary(
        self,
        patient_id: str,
        events: List[Dict],
        vitals_summary: Dict
    ) -> Dict:
        """
        Generate shift handover summary (SOAP format).
        
        Args:
            patient_id: Patient identifier
            events: List of significant events during shift
            vitals_summary: Summary of vital signs
        
        Returns:
            {
                "subjective": str,
                "objective": str,
                "assessment": str,
                "plan": str,
                "confidence": str
            }
        """
        prompt = self._create_soap_prompt(events, vitals_summary)
        
        try:
            response = self._generate(prompt)
            return self._parse_soap_response(response)
        except Exception as e:
            logger.error(f"Shift summary generation failed: {e}")
            return self._fallback_shift_summary(events)
    
    def education_qa(
        self,
        question: str,
        context: Optional[str] = None
    ) -> Dict:
        """
        Answer medical education questions (for students).
        
        Args:
            question: Student's question
            context: Optional context (case details, etc.)
        
        Returns:
            {
                "answer": str,
                "explanation": str,
                "references": List[str],
                "confidence": str
            }
        """
        prompt = self._create_education_prompt(question, context)
        
        try:
            response = self._generate(prompt, temperature=0.5)  # Higher creativity for education
            return self._parse_education_response(response)
        except Exception as e:
            logger.error(f"Education Q&A failed: {e}")
            return {"answer": "Unable to generate response. Please try again."}
    
    # Internal methods
    
    def _generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """
        Call LLM inference endpoint.
        
        Args:
            prompt: Input prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
        
        Returns:
            API response dictionary
        """
        payload = {
            "prompt": prompt,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            "top_p": 0.95,
            "stop": ["###", "\n\n\n"],
            "stream": False
        }
        
        response = requests.post(
            f"{self.base_url}/v1/completions",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        return response.json()
    
    def _create_alert_prompt(
        self,
        alert_type: str,
        vitals: Dict,
        scores: Dict,
        context: Optional[str]
    ) -> str:
        """Create prompt for alert explanation."""
        vitals_str = self._format_vitals(vitals)
        scores_str = self._format_scores(scores)
        
        prompt = f"""### Instruction:
Explain why this {alert_type} alert fired. Break down the contributing factors and suggest what clinician should monitor next. Be concise and clinical.

### Input:
Vitals: {vitals_str}
Scores: {scores_str}"""
        
        if context:
            prompt += f"\nContext: {context}"
        
        prompt += "\n\n### Response:\n"
        
        return prompt
    
    def _create_trend_prompt(self, vitals_history: List[Dict], time_window: str) -> str:
        """Create prompt for trend summarization."""
        # Format last 10 measurements
        recent = vitals_history[-10:] if len(vitals_history) > 10 else vitals_history
        trends = "\n".join([
            f"Time {i+1}: HR {v.get('hr', 'N/A')}, BP {v.get('sbp', 'N/A')}/{v.get('dbp', 'N/A')}, "
            f"SpO2 {v.get('spo2', 'N/A')}%, RR {v.get('rr', 'N/A')}, Temp {v.get('temp', 'N/A')}°C"
            for i, v in enumerate(recent)
        ])
        
        return f"""### Instruction:
Summarize the clinical trends over the last {time_window}. Identify key changes and potential concerns.

### Input:
{trends}

### Response:
"""
    
    def _create_soap_prompt(self, events: List[Dict], vitals_summary: Dict) -> str:
        """Create prompt for SOAP note generation."""
        events_str = "\n".join([f"- {e.get('description', '')}" for e in events])
        
        return f"""### Instruction:
Generate a concise SOAP note for shift handover. Include subjective, objective, assessment, and plan.

### Input:
Events during shift:
{events_str}

Vitals Summary: {vitals_summary}

### Response:
"""
    
    def _create_education_prompt(self, question: str, context: Optional[str]) -> str:
        """Create prompt for education Q&A."""
        prompt = f"""### Instruction:
You are a medical teacher for MBBS students. Answer this question clearly with clinical reasoning. Use Socratic method when appropriate.

### Question:
{question}"""
        
        if context:
            prompt += f"\n\nContext: {context}"
        
        prompt += "\n\n### Answer:\n"
        
        return prompt
    
    def _format_vitals(self, vitals: Dict) -> str:
        """Format vitals for prompt."""
        return f"HR {vitals.get('hr', 'N/A')} bpm, BP {vitals.get('sbp', 'N/A')}/{vitals.get('dbp', 'N/A')} mmHg, " \
               f"SpO2 {vitals.get('spo2', 'N/A')}%, RR {vitals.get('rr', 'N/A')}/min, Temp {vitals.get('temp', 'N/A')}°C"
    
    def _format_scores(self, scores: Dict) -> str:
        """Format clinical scores for prompt."""
        return ", ".join([f"{k.upper()} {v}" for k, v in scores.items()])
    
    def _calculate_confidence(self, response: Dict) -> str:
        """Calculate confidence level from LLM response."""
        # Simple heuristic based on completion probability
        # In production, use more sophisticated methods
        return ConfidenceLevel.MEDIUM.value  # Default to medium
    
    def _parse_alert_response(self, response: Dict) -> Dict:
        """Parse alert explanation from LLM response."""
        text = response["choices"][0]["text"].strip()
        
        # Extract sections (simple parser)
        return {
            "text": text,
            "recommendations": [],
            "sources": []
        }
    
    def _parse_trend_response(self, response: Dict) -> Dict:
        """Parse trend summary from LLM response."""
        text = response["choices"][0]["text"].strip()
        
        return {
            "summary": text,
            "key_changes": [],
            "concerns": [],
            "confidence": ConfidenceLevel.MEDIUM.value
        }
    
    def _parse_soap_response(self, response: Dict) -> Dict:
        """Parse SOAP note from LLM response."""
        text = response["choices"][0]["text"].strip()
        
        # Simple parser - in production, use more sophisticated parsing
        return {
            "subjective": "",
            "objective": "",
            "assessment": "",
            "plan": "",
            "confidence": ConfidenceLevel.MEDIUM.value
        }
    
    def _parse_education_response(self, response: Dict) -> Dict:
        """Parse education Q&A from LLM response."""
        text = response["choices"][0]["text"].strip()
        
        return {
            "answer": text,
            "explanation": "",
            "references": [],
            "confidence": ConfidenceLevel.MEDIUM.value
        }
    
    # Fallback methods (when LLM is unavailable)
    
    def _fallback_alert_explanation(self, alert_type: str, scores: Dict) -> Dict:
        """Fallback explanation when LLM unavailable."""
        return {
            "explanation": f"{alert_type} alert triggered. Scores: {scores}. Clinician review required.",
            "confidence": ConfidenceLevel.LOW.value,
            "recommendations": ["Senior clinician review", "Monitor vital trends"],
            "sources": []
        }
    
    def _fallback_trend_summary(self, vitals_history: List[Dict]) -> Dict:
        """Fallback trend summary when LLM unavailable."""
        return {
            "summary": "Vitals data available. LLM analysis unavailable.",
            "key_changes": [],
            "concerns": [],
            "confidence": ConfidenceLevel.LOW.value
        }
    
    def _fallback_shift_summary(self, events: List[Dict]) -> Dict:
        """Fallback shift summary when LLM unavailable."""
        return {
            "subjective": "Patient status",
            "objective": f"{len(events)} events recorded",
            "assessment": "See detailed vitals",
            "plan": "Continue current management",
            "confidence": ConfidenceLevel.LOW.value
        }


# Example usage
if __name__ == "__main__":
    # Initialize service
    llm = LLMService(base_url="http://localhost:8001")
    
    # Example: Explain alert
    result = llm.explain_alert(
        alert_type="NEWS2_HIGH",
        vitals={
            "hr": 115,
            "sbp": 95,
            "dbp": 60,
            "rr": 26,
            "temp": 38.8,
            "spo2": 92
        },
        scores={"news2": 8, "qsofa": 2}
    )
    
    print("Alert Explanation:")
    print(result["explanation"])
    print(f"Confidence: {result['confidence']}")
