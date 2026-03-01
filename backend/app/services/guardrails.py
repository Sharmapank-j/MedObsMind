"""
Safety Guardrails for MedObsMind LLM

Implements multiple layers of safety checks:
1. Hard-coded pattern blocking (dangerous phrases)
2. Confidence scoring
3. Medical ethics checks
4. Hallucination detection
5. Human-in-loop escalation

Ensures AI outputs are always assistive, never autonomous.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class SafetyViolationType(str, Enum):
    """Types of safety violations."""
    PRESCRIPTION = "prescription"  # Prescribing medications
    DIAGNOSIS = "diagnosis"  # Diagnosing diseases
    OVERRIDE_ALERT = "override_alert"  # Suggesting to ignore alerts
    ABSOLUTE_CERTAINTY = "absolute_certainty"  # Claiming 100% certainty
    BYPASS_CLINICIAN = "bypass_clinician"  # Advising against doctor review
    HALLUCINATION = "hallucination"  # Making up facts
    LOW_CONFIDENCE = "low_confidence"  # Uncertain output


@dataclass
class SafetyCheckResult:
    """Result of safety check."""
    is_safe: bool
    violations: List[SafetyViolationType]
    modified_output: Optional[str]
    confidence: str
    requires_review: bool
    explanation: str


class Guardrails:
    """
    Safety guardrails for dsquaremedicalmodel outputs.
    
    Implements rule-first, safety-locked approach:
    - Rules fire FIRST
    - LLM explains AFTER
    - Human decides ALWAYS
    """
    
    # Dangerous patterns (hard blocks)
    BLOCKED_PATTERNS = [
        # Prescription patterns
        (r"(prescribe|give|administer)\s+\d+\s*(mg|g|ml|units|mcg)", SafetyViolationType.PRESCRIPTION),
        (r"start\s+(patient\s+on|him|her)\s+\w+\s+\d+", SafetyViolationType.PRESCRIPTION),
        
        # Diagnosis patterns
        (r"(patient\s+has|diagnosis\s+is|diagnosed\s+with)\s+[a-z]+", SafetyViolationType.DIAGNOSIS),
        (r"(definitely|certainly)\s+(has|is)\s+\w+", SafetyViolationType.DIAGNOSIS),
        
        # Override alert patterns
        (r"(ignore|dismiss|override)\s+(the\s+)?(alert|warning)", SafetyViolationType.OVERRIDE_ALERT),
        (r"no\s+need\s+to\s+(call|inform|notify)", SafetyViolationType.OVERRIDE_ALERT),
        
        # Absolute certainty
        (r"(100%|absolutely|definitely|certainly)\s+(sure|certain|is|has)", SafetyViolationType.ABSOLUTE_CERTAINTY),
        
        # Bypass clinician
        (r"do\s+not\s+(call|inform|notify)\s+doctor", SafetyViolationType.BYPASS_CLINICIAN),
        (r"no\s+need\s+for\s+(doctor|clinician)\s+review", SafetyViolationType.BYPASS_CLINICIAN),
    ]
    
    # Uncertainty markers (good - show appropriate caution)
    UNCERTAINTY_MARKERS = [
        "may indicate", "could suggest", "consider", "possible", "potential",
        "consistent with", "suggestive of", "compatible with", "might be"
    ]
    
    # Required phrases for clinical outputs
    REQUIRED_PHRASES = [
        "clinician review", "doctor review", "medical review",
        "clinical assessment", "doctor assessment"
    ]
    
    def __init__(
        self,
        confidence_threshold_high: float = 0.85,
        confidence_threshold_low: float = 0.60
    ):
        """
        Initialize guardrails.
        
        Args:
            confidence_threshold_high: Threshold for high confidence
            confidence_threshold_low: Threshold below which requires review
        """
        self.confidence_high = confidence_threshold_high
        self.confidence_low = confidence_threshold_low
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), violation_type)
            for pattern, violation_type in self.BLOCKED_PATTERNS
        ]
    
    def check_safety(
        self,
        llm_output: str,
        input_data: Optional[Dict] = None,
        confidence_score: Optional[float] = None
    ) -> SafetyCheckResult:
        """
        Comprehensive safety check on LLM output.
        
        Args:
            llm_output: Generated text from LLM
            input_data: Original input data (for hallucination detection)
            confidence_score: Confidence score (0-1)
        
        Returns:
            SafetyCheckResult with all safety checks
        """
        violations = []
        modified_output = llm_output
        requires_review = False
        
        # 1. Check for dangerous patterns
        pattern_violations = self._check_dangerous_patterns(llm_output)
        if pattern_violations:
            violations.extend(pattern_violations)
            modified_output = self._sanitize_output(llm_output, pattern_violations)
        
        # 2. Check confidence level
        if confidence_score is not None:
            if confidence_score < self.confidence_low:
                violations.append(SafetyViolationType.LOW_CONFIDENCE)
                requires_review = True
        
        # 3. Check for hallucinations
        if input_data:
            hallucination_detected = self._check_hallucination(llm_output, input_data)
            if hallucination_detected:
                violations.append(SafetyViolationType.HALLUCINATION)
                requires_review = True
        
        # 4. Check for required safety phrases
        if not self._has_clinician_review_phrase(llm_output):
            # Add clinician review reminder
            modified_output += "\n\n**Clinician review required for all clinical decisions.**"
        
        # 5. Determine confidence level
        confidence = self._classify_confidence(
            llm_output,
            confidence_score,
            bool(violations)
        )
        
        # 6. Determine if safe
        is_safe = len(violations) == 0 or all(
            v in [SafetyViolationType.LOW_CONFIDENCE] for v in violations
        )
        
        # 7. Create explanation
        explanation = self._create_explanation(violations, confidence)
        
        return SafetyCheckResult(
            is_safe=is_safe,
            violations=violations,
            modified_output=modified_output if is_safe else None,
            confidence=confidence,
            requires_review=requires_review,
            explanation=explanation
        )
    
    def _check_dangerous_patterns(self, text: str) -> List[SafetyViolationType]:
        """Check for dangerous patterns in output."""
        violations = []
        
        for pattern, violation_type in self.compiled_patterns:
            if pattern.search(text):
                violations.append(violation_type)
                logger.warning(f"Safety violation detected: {violation_type}")
        
        return violations
    
    def _sanitize_output(
        self,
        text: str,
        violations: List[SafetyViolationType]
    ) -> str:
        """Sanitize output by removing dangerous content."""
        # For critical violations, return generic safe response
        critical_violations = [
            SafetyViolationType.PRESCRIPTION,
            SafetyViolationType.DIAGNOSIS,
            SafetyViolationType.OVERRIDE_ALERT,
            SafetyViolationType.BYPASS_CLINICIAN
        ]
        
        if any(v in critical_violations for v in violations):
            return "Clinical assessment required. Please review patient data with attending clinician."
        
        return text
    
    def _check_hallucination(self, output: str, input_data: Dict) -> bool:
        """
        Check if output mentions vitals/data not in input.
        
        Simple heuristic: Extract vitals from output and verify against input.
        """
        # Extract vital signs mentioned in output
        output_lower = output.lower()
        
        # Check for specific vitals
        vitals_to_check = {
            "heart rate": input_data.get("vitals", {}).get("hr"),
            "blood pressure": input_data.get("vitals", {}).get("sbp"),
            "temperature": input_data.get("vitals", {}).get("temp"),
            "respiratory rate": input_data.get("vitals", {}).get("rr"),
            "spo2": input_data.get("vitals", {}).get("spo2"),
            "oxygen saturation": input_data.get("vitals", {}).get("spo2"),
        }
        
        for vital_name, vital_value in vitals_to_check.items():
            if vital_name in output_lower and vital_value is None:
                logger.warning(f"Possible hallucination: {vital_name} mentioned but not in input")
                return True
        
        return False
    
    def _has_clinician_review_phrase(self, text: str) -> bool:
        """Check if output includes clinician review reminder."""
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in self.REQUIRED_PHRASES)
    
    def _classify_confidence(
        self,
        text: str,
        confidence_score: Optional[float],
        has_violations: bool
    ) -> str:
        """Classify confidence level of output."""
        if has_violations:
            return "low"
        
        if confidence_score is not None:
            if confidence_score >= self.confidence_high:
                return "high"
            elif confidence_score >= self.confidence_low:
                return "medium"
            else:
                return "low"
        
        # Heuristic based on uncertainty markers
        text_lower = text.lower()
        uncertainty_count = sum(
            1 for marker in self.UNCERTAINTY_MARKERS if marker in text_lower
        )
        
        if uncertainty_count >= 3:
            return "medium"
        elif uncertainty_count >= 1:
            return "medium"
        else:
            return "high"  # Assume high if well-formed
    
    def _create_explanation(
        self,
        violations: List[SafetyViolationType],
        confidence: str
    ) -> str:
        """Create human-readable explanation of safety check."""
        if not violations:
            return f"Output passed safety checks (confidence: {confidence})"
        
        violation_messages = {
            SafetyViolationType.PRESCRIPTION: "Output contained prescription language",
            SafetyViolationType.DIAGNOSIS: "Output contained diagnostic language",
            SafetyViolationType.OVERRIDE_ALERT: "Output suggested ignoring alerts",
            SafetyViolationType.ABSOLUTE_CERTAINTY: "Output claimed absolute certainty",
            SafetyViolationType.BYPASS_CLINICIAN: "Output suggested bypassing clinician",
            SafetyViolationType.HALLUCINATION: "Output may contain hallucinated facts",
            SafetyViolationType.LOW_CONFIDENCE: "Output confidence below threshold"
        }
        
        messages = [violation_messages.get(v, str(v)) for v in violations]
        return f"Safety violations: {', '.join(messages)}"
    
    def transform_to_assistive_language(self, text: str) -> str:
        """
        Transform autonomous language to assistive language.
        
        Example:
        "Patient has sepsis" → "Clinical features suggest possible sepsis"
        "Prescribe antibiotics" → "Consider antibiotic therapy per protocol"
        """
        # Replace absolute statements with conditional ones
        transformations = [
            (r"patient\s+has\s+(\w+)", r"clinical features suggest possible \1"),
            (r"diagnosis\s+is\s+(\w+)", r"findings consistent with \1"),
            (r"prescribe\s+(\w+)", r"consider \1 therapy per hospital protocol"),
            (r"give\s+(\w+)", r"may consider \1 if clinically indicated"),
            (r"(definitely|certainly)\s+", r"likely "),
        ]
        
        transformed = text
        for pattern, replacement in transformations:
            transformed = re.sub(pattern, replacement, transformed, flags=re.IGNORECASE)
        
        return transformed


# Example usage
if __name__ == "__main__":
    # Initialize guardrails
    guardrails = Guardrails()
    
    # Test cases
    test_outputs = [
        ("Patient has sepsis. Prescribe ceftriaxone 1g IV.", "Dangerous - prescription + diagnosis"),
        ("Clinical features suggest possible sepsis. Consider sepsis protocol per hospital guidelines. Clinician review required.", "Safe - assistive language"),
        ("Ignore the NEWS2 alert, it's probably nothing.", "Dangerous - override alert"),
        ("The heart rate is 150 bpm (actual: 85 in input)", "Dangerous - hallucination"),
    ]
    
    for output, description in test_outputs:
        print(f"\nTest: {description}")
        print(f"Output: {output[:80]}...")
        
        # Check safety (with mock input data for hallucination detection)
        result = guardrails.check_safety(
            output,
            input_data={"vitals": {"hr": 85, "sbp": 120}},
            confidence_score=0.75
        )
        
        print(f"Safe: {result.is_safe}")
        print(f"Violations: {result.violations}")
        print(f"Confidence: {result.confidence}")
        print(f"Requires Review: {result.requires_review}")
        print(f"Explanation: {result.explanation}")
