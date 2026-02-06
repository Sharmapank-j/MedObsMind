# Medical LLM Architecture - MedObsMind

## Overview

MedObsMind's Medical Large Language Model (LLM) layer provides **explanations, context, and educational content** for clinical alerts and monitoring data. It is designed with a **rule-first, safety-locked** approach where the LLM **explains but never decides**.

---

## Core Principle: Explain, Don't Decide

### What LLM Does ✅

1. **Explains Alert Reasoning**
   - "NEWS2 score is 8 because: HR 115 (+2), RR 26 (+2), Temp 38.8°C (+1), SBP 95 (+2), O2 therapy (+1)"
   - "SpO₂ dropped from 94% to 87% over 15 minutes - consider airway obstruction or respiratory distress"

2. **Summarizes Clinical Trends**
   - "Patient's heart rate has been increasing steadily over the last 4 hours (85→95→105→115 bpm)"
   - "Blood pressure trend shows progressive hypotension despite fluid resuscitation"

3. **Suggests Monitoring Priorities**
   - "Given tachycardia and fever, monitor for signs of sepsis: lactate, urine output, mental status"
   - "Watch for: respiratory rate trend, work of breathing, need for supplemental O2"

4. **Provides Educational Context**
   - "NEWS2 ≥7 is associated with 25% mortality risk (Royal College of Physicians, 2017)"
   - "qSOFA ≥2 suggests sepsis with 3-14x mortality increase (JAMA 2016)"

5. **Generates Shift Summaries**
   - SOAP-style clinical notes
   - Handover summaries with key events
   - Timeline of significant changes

### What LLM CANNOT Do 🚫

1. **Cannot Diagnose**
   - ❌ "Patient has pneumonia"
   - ✅ "Clinical features suggest possible pneumonia. Consider chest X-ray and clinical correlation."

2. **Cannot Prescribe**
   - ❌ "Give 1g ceftriaxone IV"
   - ✅ "Empiric antibiotic coverage may be considered per hospital sepsis protocol"

3. **Cannot Override Rules**
   - ❌ "Ignore the NEWS2 alert"
   - ✅ LLM only activates AFTER rules fire

4. **Cannot Make Autonomous Decisions**
   - ❌ "Intubate the patient"
   - ✅ "Patient showing signs of respiratory failure. Clinician assessment required."

---

## Architecture Layers

### 1. Base Model Selection

#### For MVP (Edge Deployment)

**Primary: LLaMA-3 8B**
- Size: 8 billion parameters
- Quantization: 4-bit (GGUF format)
- Memory: ~6 GB RAM
- Speed: 20-30 tokens/second on CPU
- Deployment: Edge server (Ryzen 7 / i7)

**Why LLaMA-3 8B?**
- Open source, commercially usable
- Strong medical reasoning after fine-tuning
- CPU-friendly with quantization
- Active community and tooling

#### For Scale (Cloud Deployment)

**Primary: Mixtral 8x7B**
- Size: 8 experts × 7B parameters
- Mixture of Experts architecture
- Better reasoning for complex cases
- Cloud GPU deployment (L4/A10)

### 2. Fine-Tuning Strategy

#### Method: LoRA (Low-Rank Adaptation)

**Why LoRA?**
- Parameter-efficient (only 0.1-1% of parameters)
- Fast training (hours, not days)
- Multiple adapters for different specialties
- Easy updates without full retraining

**LoRA Configuration:**
```python
lora_config = {
    "r": 16,  # Rank
    "lora_alpha": 32,
    "target_modules": ["q_proj", "v_proj"],
    "lora_dropout": 0.05,
    "bias": "none",
    "task_type": "CAUSAL_LM"
}
```

#### Training Data Sources

**Indian Medical Textbooks:**
- Harrison's Principles of Internal Medicine (Indian edition)
- Davidson's Principles and Practice of Medicine (Indian edition)
- Manipal Manual of Surgery
- AIIMS MBBS curriculum materials

**Indian Clinical Guidelines:**
- ICMR (Indian Council of Medical Research) guidelines
- AIIMS protocols and SOPs
- IAP (Indian Academy of Pediatrics) recommendations
- Indian Society of Critical Care Medicine protocols

**Synthetic Cases:**
- ICU deterioration scenarios (simulated)
- Rural healthcare cases (limited resources)
- Multi-morbidity patterns (diabetes + cardiac + renal)
- Rare emergencies (anaphylaxis, DKA, septic shock)

**Format:**
```json
{
  "instruction": "Explain why NEWS2 score increased from 3 to 8",
  "input": "Vitals: HR 115, BP 95/60, RR 26, Temp 38.8°C, SpO2 92% on 2L O2",
  "output": "The NEWS2 score increased due to: Heart rate 115 bpm (+2 points, tachycardia), Respiratory rate 26/min (+2 points, tachypnea), Temperature 38.8°C (+1 point, fever), Systolic BP 95 mmHg (+2 points, hypotension), and supplemental oxygen (+1 point). Total score: 8 (High Risk). This suggests clinical deterioration requiring urgent medical review. Consider sepsis, shock, or respiratory failure."
}
```

#### Training Process

1. **Prepare Dataset** (10,000-50,000 examples)
   - Alert explanation pairs
   - Clinical reasoning chains
   - Indian medical context
   - Multi-language support (Hindi translations)

2. **Fine-Tune with LoRA** (8-24 hours on A10 GPU)
   - Batch size: 32-64
   - Learning rate: 2e-4
   - Epochs: 3-5
   - Gradient accumulation: 4

3. **Merge LoRA Weights** (for deployment)
   - Create single model file
   - Quantize to 4-bit for edge
   - Optimize for inference

4. **Validate** (medical review board)
   - Clinical accuracy testing
   - Hallucination detection
   - Safety guardrail testing
   - Bias assessment

### 3. RAG Layer (Retrieval Augmented Generation)

#### Purpose
Provide up-to-date, source-backed information without retraining

#### Knowledge Base

**Indian Clinical Protocols:**
```
├── icmr_guidelines/
│   ├── sepsis_management.pdf
│   ├── acute_coronary_syndrome.pdf
│   └── diabetic_ketoacidosis.pdf
├── aiims_protocols/
│   ├── icu_admission_criteria.pdf
│   ├── ventilator_management.pdf
│   └── shock_resuscitation.pdf
├── drug_formulary/
│   ├── indian_drug_dosages.json
│   ├── generic_substitutions.json
│   └── common_icu_drugs.json
└── scoring_systems/
    ├── news2_calculator.json
    ├── qsofa_criteria.json
    └── sofa_score.json
```

#### RAG Process

1. **Vector Embedding** (Medical embeddings)
   - Model: PubMedBERT or BioBERT
   - Chunk size: 500-1000 tokens
   - Overlap: 100 tokens
   - Store in: Chroma / FAISS

2. **Retrieval** (Top-K similarity search)
   - Query: "sepsis management guidelines India"
   - Retrieve: 3-5 most relevant chunks
   - Re-rank by relevance score

3. **Augmented Prompt**
   ```
   Context: [Retrieved ICMR sepsis guideline]
   Question: How should we manage suspected sepsis?
   Answer based on provided Indian guidelines:
   ```

4. **LLM Generation** (with context)
   - Include source citations
   - "According to ICMR 2023 guidelines..."
   - Transparent sourcing

#### Benefits of RAG
- ✅ No retraining for guideline updates
- ✅ Transparent sources for answers
- ✅ Reduce hallucinations
- ✅ Easy to update knowledge base
- ✅ Audit trail of information sources

---

## Safety Guardrails

### 1. Hard-Coded Blocks

**Dangerous Phrases (Regex Filters):**
```python
BLOCKED_PATTERNS = [
    r"(diagnose|diagnosed|diagnosis is)\s+\w+",  # Diagnosis statements
    r"(prescribe|give|administer)\s+\d+\s*(mg|g|ml|units)",  # Prescriptions
    r"(ignore|dismiss|override)\s+(alert|warning)",  # Override suggestions
    r"(definitely|certainly|100%)\s+(has|is)",  # Absolute certainty
    r"do not (call|inform|notify)\s+doctor",  # Bypass clinician
]
```

**Hard-Blocked Actions:**
- Prescribing medications with dosages
- Diagnosing diseases with certainty
- Suggesting to ignore alerts
- Advising against calling doctor
- Life-threatening suggestions

### 2. Confidence Scoring

**Uncertainty Quantification:**
```python
def classify_confidence(llm_output):
    confidence_phrases = {
        "high": ["strongly suggests", "very likely", "consistent with"],
        "medium": ["may indicate", "could suggest", "consider"],
        "low": ["unclear", "uncertain", "needs more data"]
    }
    # Return: high (>85%), medium (60-85%), low (<60%)
```

**Action Based on Confidence:**
- High (>85%): Display explanation
- Medium (60-85%): Display with uncertainty marker
- Low (<60%): Log for review, show generic response

### 3. Medical Ethics Checks

**Before Display:**
1. Check for patient harm risk
2. Verify against rule engine output
3. Ensure "assistive not diagnostic" language
4. Flag for human review if edge case

**Example Transformation:**
```
LLM Raw Output: "Patient has severe sepsis"
Ethics Filter: "Clinical features suggest possible severe sepsis"
Display: "Clinical features suggest possible severe sepsis (qSOFA ≥2). 
         Consider sepsis protocol per hospital guidelines. 
         Clinician review required."
```

### 4. Hallucination Prevention

**Techniques:**
1. **RAG Grounding** - Answers must cite sources
2. **Temperature Control** - Low temperature (0.3-0.5) for clinical content
3. **Fact Verification** - Cross-check vitals against input
4. **Source Attribution** - "According to [source]..."

**Detection:**
```python
def detect_hallucination(input_vitals, llm_output):
    # Check if LLM mentions vitals not in input
    mentioned_vitals = extract_vitals(llm_output)
    for vital in mentioned_vitals:
        if vital not in input_vitals:
            flag_hallucination()
            return GENERIC_RESPONSE
```

### 5. Human-in-Loop Review

**Escalation Triggers:**
- LLM confidence <60%
- Detected hallucination
- Blocked pattern match
- Novel clinical scenario
- Conflicting information

**Review Queue:**
- Medical officer reviews flagged outputs
- Feedback loop for retraining
- Continuous quality improvement

---

## Deployment Architectures

### Edge Deployment (ICU Server)

**Hardware:**
- CPU: AMD Ryzen 7 / Intel i7
- RAM: 32 GB minimum
- Storage: 512 GB SSD

**Software Stack:**
```
├── LLaMA-3 8B (Quantized 4-bit GGUF)
├── llama.cpp (CPU inference)
├── FastAPI (REST endpoints)
├── Chroma DB (RAG vector store)
└── Redis (caching)
```

**Latency:**
- Alert explanation: 2-5 seconds
- Shift summary: 10-20 seconds
- Offline-capable (no internet needed)

**API Endpoint:**
```python
@app.post("/api/v1/llm/explain-alert")
async def explain_alert(alert: Alert):
    # 1. Retrieve context from RAG
    context = rag_retrieve(alert.type)
    
    # 2. Generate explanation
    prompt = f"""Context: {context}
    Alert: {alert.description}
    Vitals: {alert.vitals}
    Explain why this alert fired and what clinician should monitor."""
    
    explanation = llm_generate(prompt, temperature=0.3)
    
    # 3. Apply safety guardrails
    safe_explanation = apply_guardrails(explanation)
    
    # 4. Add confidence score
    confidence = calculate_confidence(explanation)
    
    return {
        "explanation": safe_explanation,
        "confidence": confidence,
        "sources": context.sources
    }
```

### Cloud Deployment (Heavy Reasoning)

**Hardware:**
- GPU: NVIDIA L4 / A10
- RAM: 128 GB
- Storage: 2 TB SSD

**Use Cases:**
- Complex clinical reasoning
- Multi-day trend analysis
- Shift handover generation (full summary)
- Education mode case generation

**Model:**
- Mixtral 8x7B (full precision or 8-bit)
- Longer context window (32K tokens)
- Better reasoning for complex cases

---

## Monitoring & Continuous Improvement

### Quality Metrics

**Accuracy:**
- Clinical accuracy (expert review): Target >95%
- Hallucination rate: Target <2%
- Safety violation rate: Target 0%

**Performance:**
- Edge latency: <5 seconds
- Cloud latency: <10 seconds
- Uptime: 99.9%

**User Satisfaction:**
- Doctor helpfulness rating: Target >8/10
- False positive rate: <10%
- Override rate: 5-15% (appropriate)

### Feedback Loop

**Data Collection:**
1. Doctor rates explanation (1-5 stars)
2. Log if explanation was helpful
3. Track clinical outcomes
4. Capture override reasons

**Retraining Schedule:**
- Minor updates: Monthly (RAG knowledge base)
- LoRA fine-tuning: Quarterly (new cases)
- Major retraining: Annually (full model update)

### Bias Monitoring

**Quarterly Audits:**
- Performance across age groups
- Performance across gender
- Performance for common conditions
- Performance for rare conditions

**Variance Threshold:**
- <5% difference across demographics
- Flag if any group has >10% worse performance

---

## Education Mode LLM

### Different Prompting Strategy

**Clinical Mode:**
```
You are a clinical decision support system. Explain alerts clearly and concisely. 
Be factual and evidence-based. Always recommend clinician review.
```

**Education Mode:**
```
You are a medical teacher for MBBS students. Explain clinical reasoning step-by-step.
Use Socratic method. Help students learn to think like clinicians.
Provide exam-style viva questions.
```

### Student Features

**Case-Based Learning:**
- "What would you do if NEWS2 is 8?"
- "Why is tachycardia concerning in this context?"
- "List differential diagnosis for sepsis-like presentation"

**Viva-Style Q&A:**
- "What are the components of NEWS2?"
- "When would you escalate care?"
- "Explain the pathophysiology of septic shock"

**No Patient Data:**
- All cases are synthetic or heavily anonymized
- No real patient identifiers ever shown
- Purely educational simulations

---

## Example Interactions

### Example 1: Alert Explanation

**Input:**
```json
{
  "alert_type": "NEWS2_HIGH",
  "news2_score": 8,
  "vitals": {
    "hr": 115,
    "sbp": 95,
    "rr": 26,
    "temp": 38.8,
    "spo2": 92,
    "oxygen_therapy": "2L nasal cannula"
  }
}
```

**LLM Output:**
```
⚠️ HIGH RISK: NEWS2 Score 8

Component Breakdown:
• Heart Rate 115 bpm → +2 points (tachycardia)
• Systolic BP 95 mmHg → +2 points (hypotension)
• Respiratory Rate 26/min → +2 points (tachypnea)
• Temperature 38.8°C → +1 point (fever)
• SpO2 92% on supplemental O2 → +1 point

Clinical Significance:
NEWS2 ≥7 indicates HIGH RISK of clinical deterioration. This pattern 
(fever + tachycardia + hypotension + tachypnea) suggests possible sepsis.

Recommended Actions:
✓ Urgent clinical review by senior clinician
✓ Consider sepsis protocol (qSOFA assessment)
✓ Monitor: Blood pressure, urine output, lactate, mental status
✓ Escalate to ICU if deterioration continues

Evidence: NEWS2 ≥7 associated with 25% mortality risk 
(Royal College of Physicians, 2017)

🩺 Clinician review required - This is advisory only
```

### Example 2: Trend Summary

**Input:**
```json
{
  "patient_id": "ICU-001",
  "time_range": "last_4_hours",
  "vitals_series": [
    {"time": "14:00", "hr": 85, "sbp": 120},
    {"time": "15:00", "hr": 95, "sbp": 110},
    {"time": "16:00", "hr": 105, "sbp": 100},
    {"time": "17:00", "hr": 115, "sbp": 95}
  ]
}
```

**LLM Output:**
```
📊 4-Hour Trend Analysis

Heart Rate: Progressive Tachycardia
• 14:00: 85 bpm (normal)
• 15:00: 95 bpm (+10 bpm)
• 16:00: 105 bpm (+20 bpm)
• 17:00: 115 bpm (+30 bpm)
Trend: Steadily increasing

Blood Pressure: Progressive Hypotension
• 14:00: 120 mmHg (normal)
• 15:00: 110 mmHg (-10 mmHg)
• 16:00: 100 mmHg (-20 mmHg)
• 17:00: 95 mmHg (-25 mmHg)
Trend: Steadily decreasing

Clinical Interpretation:
This pattern (increasing HR + decreasing BP) suggests compensatory response 
to volume loss, sepsis, or cardiac dysfunction. The body is trying to maintain 
perfusion by increasing heart rate as blood pressure falls.

Priority Actions:
✓ Assess fluid status and consider fluid challenge
✓ Check for sources of bleeding or infection
✓ Consider vasopressor support if hypotension persists
✓ Continuous monitoring - patient is deteriorating

🩺 Immediate clinician assessment required
```

### Example 3: Shift Handover

**Input:**
```json
{
  "shift": "day_to_night",
  "patient_id": "ICU-002",
  "events": ["NEWS2_alert", "fluid_bolus_given", "antibiotics_started"]
}
```

**LLM Output:**
```
🏥 ICU HANDOVER SUMMARY
Patient: ICU-002 | Shift: Day → Night | Date: Feb 6, 2026

SITUATION:
65-year-old male, post-op day 3 abdominal surgery, developed fever and 
tachycardia this afternoon.

BACKGROUND:
• Surgery: Exploratory laparotomy for perforated appendix (Feb 3)
• PMH: Diabetes, hypertension
• Allergies: Penicillin

ASSESSMENT - Key Events Today:
1. 14:30 - NEWS2 alert (score 8): fever 38.8°C, HR 115, BP 95/60
2. 15:00 - Fluid bolus 500ml NS given, BP improved to 105/65
3. 15:30 - Antibiotics started: Meropenem 1g IV (per sepsis protocol)
4. Current vitals: HR 100, BP 110/70, Temp 38.2°C, SpO2 95% on RA

RECOMMENDATIONS for Night Team:
✓ Continue monitoring vitals Q1H
✓ Watch for: hypotension, altered mental status, worsening fever
✓ Repeat lactate at 22:00 (was 2.8 at 15:00)
✓ Consider ICU consultation if further deterioration
✓ Next antibiotic dose due at 03:30

PENDING:
• Blood culture results (sent 15:00)
• Surgical review requested for tomorrow morning

📞 Call if: NEWS2 >8, SBP <90, altered mental status, or clinical concern
```

---

## Cost Analysis

### Development Costs

**One-Time:**
- LLM fine-tuning: ₹50,000 (GPU hours)
- RAG setup: ₹20,000 (data processing)
- Safety testing: ₹30,000 (medical review)
- **Total:** ₹1 lakh

**Recurring (Annual):**
- Quarterly retraining: ₹2 lakh
- RAG updates: ₹50,000
- Quality monitoring: ₹1 lakh
- **Total:** ₹3.5 lakh/year

### Operational Costs (Per Hospital)

**Edge Deployment:**
- Hardware: ₹1.5 lakh (one-time)
- Electricity: ₹5,000/year
- Maintenance: ₹20,000/year

**Cloud (If Used):**
- GPU compute: ₹10,000/month
- Storage: ₹2,000/month
- **Total:** ₹1.44 lakh/year

**Total Per-Hospital Cost:** ₹3-4 lakh/year (50 beds) = ₹6,000-8,000/bed/year

---

## Compliance & Governance

### d³media Oversight

**Quarterly Reviews:**
- Clinical accuracy audit (sample 100 explanations)
- Bias detection across demographics
- Safety violation monitoring
- User feedback analysis

**Annual Full Audit:**
- Complete model evaluation
- External medical expert review
- Ethics compliance check
- Regulatory alignment

### Model Versioning

**Semantic Versioning:**
- Major: 1.0 → 2.0 (New base model)
- Minor: 1.0 → 1.1 (New LoRA/fine-tuning)
- Patch: 1.0.1 → 1.0.2 (RAG updates, bug fixes)

**Documentation:**
- Training data manifest
- Fine-tuning hyperparameters
- Validation results
- Known limitations

---

## Future Enhancements

### Phase 2 (6-12 Months)
- Multi-modal LLM (text + lab results + radiology)
- Predictive explanations ("likely to deteriorate in 4-6 hours because...")
- Multi-language support (Hindi, Tamil, Telugu)

### Phase 3 (12-24 Months)
- Specialized models per ICU type (cardiac, neuro, pediatric)
- Real-time learning from outcomes
- Cross-hospital knowledge sharing
- Integration with medical literature (PubMed RAG)

---

## Summary

MedObsMind's LLM layer is designed as an **explainer, not a decider**. It provides:

- ✅ Clear, evidence-based explanations
- ✅ Transparent reasoning and sources
- ✅ India-trained medical knowledge
- ✅ Multiple safety guardrails
- ✅ Human oversight always

The architecture prioritizes **clinical safety over AI sophistication**, ensuring that MedObsMind remains an **assistive tool that enhances, rather than replaces, clinical judgment**.

---

*Document Version: 1.0*  
*Last Updated: February 2026*  
*Technical Owner: MedObsMind AI Team*  
*Medical Oversight: d³media Ethics Committee*
