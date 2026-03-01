"""
NEWS2 (National Early Warning Score 2) Implementation

The NEWS2 is a UK-developed standardized scoring system for assessing acute illness severity.
It helps identify patients at risk of deterioration.

Score ranges:
- 0-4: Low risk
- 5-6: Medium risk (ward-based response)
- 7+: High risk (urgent clinical review)

Reference: Royal College of Physicians (2017)
"""

from typing import Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class NEWS2Result:
    """NEWS2 calculation result"""
    total_score: int
    risk_level: str  # low, medium, high
    component_scores: Dict[str, int]
    recommendations: list
    requires_escalation: bool


class NEWS2Calculator:
    """
    NEWS2 (National Early Warning Score 2) calculator.
    
    Clinical parameters scored:
    1. Respiratory Rate (RR)
    2. Oxygen Saturation (SpO₂)
    3. Supplemental Oxygen
    4. Temperature
    5. Systolic Blood Pressure (SBP)
    6. Heart Rate (HR)
    7. Level of Consciousness (AVPU)
    """
    
    # Scoring tables based on NEWS2 guidelines
    
    RESPIRATORY_RATE_SCORES = {
        (0, 8): 3,      # ≤8
        (9, 11): 1,     # 9-11
        (12, 20): 0,    # 12-20 (normal)
        (21, 24): 2,    # 21-24
        (25, 999): 3,   # ≥25
    }
    
    SPO2_SCORES_SCALE_1 = {  # For patients NOT on oxygen target range
        (0, 91): 3,     # ≤91
        (92, 93): 2,    # 92-93
        (94, 95): 1,    # 94-95
        (96, 100): 0,   # ≥96 (normal)
    }
    
    SPO2_SCORES_SCALE_2 = {  # For patients with COPD (hypercapnic respiratory failure)
        (0, 83): 3,     # ≤83
        (84, 85): 2,    # 84-85
        (86, 87): 1,    # 86-87
        (88, 92): 0,    # 88-92 (target for COPD)
        (93, 94): 1,    # 93-94
        (95, 96): 2,    # 95-96
        (97, 100): 3,   # ≥97
    }
    
    TEMPERATURE_SCORES = {
        (0, 35.0): 3,        # ≤35.0
        (35.1, 36.0): 1,     # 35.1-36.0
        (36.1, 38.0): 0,     # 36.1-38.0 (normal)
        (38.1, 39.0): 1,     # 38.1-39.0
        (39.1, 999): 2,      # ≥39.1
    }
    
    SYSTOLIC_BP_SCORES = {
        (0, 90): 3,         # ≤90
        (91, 100): 2,       # 91-100
        (101, 110): 1,      # 101-110
        (111, 219): 0,      # 111-219 (normal)
        (220, 999): 3,      # ≥220
    }
    
    HEART_RATE_SCORES = {
        (0, 40): 3,         # ≤40
        (41, 50): 1,        # 41-50
        (51, 90): 0,        # 51-90 (normal)
        (91, 110): 1,       # 91-110
        (111, 130): 2,      # 111-130
        (131, 999): 3,      # ≥131
    }
    
    CONSCIOUSNESS_SCORES = {
        "A": 0,  # Alert
        "V": 3,  # Response to Voice
        "P": 3,  # Response to Pain
        "U": 3,  # Unresponsive
    }
    
    @staticmethod
    def _score_from_range(value: float, score_table: Dict[Tuple[float, float], int]) -> int:
        """Get score from a range-based scoring table"""
        for (min_val, max_val), score in score_table.items():
            if min_val <= value <= max_val:
                return score
        return 0
    
    def calculate(
        self,
        respiratory_rate: Optional[float] = None,
        spo2: Optional[float] = None,
        supplemental_oxygen: bool = False,
        temperature: Optional[float] = None,
        systolic_bp: Optional[float] = None,
        heart_rate: Optional[float] = None,
        consciousness_level: Optional[str] = None,
        use_scale_2: bool = False  # For COPD patients
    ) -> NEWS2Result:
        """
        Calculate NEWS2 score.
        
        Args:
            respiratory_rate: Breaths per minute
            spo2: Oxygen saturation (%)
            supplemental_oxygen: Whether patient is on supplemental O2
            temperature: Body temperature (°C)
            systolic_bp: Systolic blood pressure (mmHg)
            heart_rate: Heart rate (bpm)
            consciousness_level: AVPU scale (A/V/P/U)
            use_scale_2: Use Scale 2 for SpO₂ (COPD patients)
        
        Returns:
            NEWS2Result with total score, risk level, and recommendations
        """
        component_scores = {}
        total = 0
        
        # 1. Respiratory Rate
        if respiratory_rate is not None:
            rr_score = self._score_from_range(respiratory_rate, self.RESPIRATORY_RATE_SCORES)
            component_scores["respiratory_rate"] = rr_score
            total += rr_score
        
        # 2. Oxygen Saturation
        if spo2 is not None:
            spo2_table = self.SPO2_SCORES_SCALE_2 if use_scale_2 else self.SPO2_SCORES_SCALE_1
            spo2_score = self._score_from_range(spo2, spo2_table)
            component_scores["spo2"] = spo2_score
            total += spo2_score
        
        # 3. Supplemental Oxygen (2 points if on oxygen)
        oxygen_score = 2 if supplemental_oxygen else 0
        component_scores["supplemental_oxygen"] = oxygen_score
        total += oxygen_score
        
        # 4. Temperature
        if temperature is not None:
            temp_score = self._score_from_range(temperature, self.TEMPERATURE_SCORES)
            component_scores["temperature"] = temp_score
            total += temp_score
        
        # 5. Systolic Blood Pressure
        if systolic_bp is not None:
            sbp_score = self._score_from_range(systolic_bp, self.SYSTOLIC_BP_SCORES)
            component_scores["systolic_bp"] = sbp_score
            total += sbp_score
        
        # 6. Heart Rate
        if heart_rate is not None:
            hr_score = self._score_from_range(heart_rate, self.HEART_RATE_SCORES)
            component_scores["heart_rate"] = hr_score
            total += hr_score
        
        # 7. Level of Consciousness
        if consciousness_level:
            consciousness_score = self.CONSCIOUSNESS_SCORES.get(consciousness_level.upper(), 0)
            component_scores["consciousness"] = consciousness_score
            total += consciousness_score
        
        # Determine risk level and recommendations
        if total == 0:
            risk_level = "low"
            recommendations = ["Continue routine monitoring"]
            requires_escalation = False
        elif 1 <= total <= 4:
            risk_level = "low"
            recommendations = [
                "Continue routine monitoring",
                "Assess frequency of monitoring"
            ]
            requires_escalation = False
        elif 5 <= total <= 6:
            risk_level = "medium"
            recommendations = [
                "Increase monitoring frequency",
                "Inform registered nurse",
                "Urgent review by ward-based doctor"
            ]
            requires_escalation = True
        else:  # 7+
            risk_level = "high"
            recommendations = [
                "Continuous monitoring",
                "Emergency assessment by clinical team",
                "Consider ICU/HDU transfer",
                "Alert senior clinician immediately"
            ]
            requires_escalation = True
        
        return NEWS2Result(
            total_score=total,
            risk_level=risk_level,
            component_scores=component_scores,
            recommendations=recommendations,
            requires_escalation=requires_escalation
        )
    
    @staticmethod
    def interpret_score(score: int) -> str:
        """Get clinical interpretation of NEWS2 score"""
        if score == 0:
            return "No acute illness detected"
        elif 1 <= score <= 4:
            return "Low clinical risk - routine monitoring"
        elif 5 <= score <= 6:
            return "Medium risk - increased monitoring and clinical review required"
        else:
            return "High risk - urgent or emergency clinical assessment required"


# Example usage
if __name__ == "__main__":
    calculator = NEWS2Calculator()
    
    # Example: Patient with mild tachycardia and low-grade fever
    result = calculator.calculate(
        respiratory_rate=18,
        spo2=96,
        supplemental_oxygen=False,
        temperature=38.2,
        systolic_bp=125,
        heart_rate=105,
        consciousness_level="A"
    )
    
    print(f"NEWS2 Score: {result.total_score}")
    print(f"Risk Level: {result.risk_level}")
    print(f"Component Scores: {result.component_scores}")
    print(f"Recommendations: {result.recommendations}")
