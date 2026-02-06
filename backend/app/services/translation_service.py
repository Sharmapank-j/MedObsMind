"""
Translation Service for MedObsMind

Provides multi-language support for Indian languages:
- Hindi, Tamil, Telugu, Bengali, Marathi, etc.
- Medical term preservation
- Code-mixing support
- Transliteration

Ensures medical information is accessible in user's preferred language.
"""

import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    ODIA = "or"
    ASSAMESE = "as"
    URDU = "ur"


@dataclass
class TranslationResult:
    """Result of translation."""
    translated_text: str
    source_lang: str
    target_lang: str
    confidence: float
    preserved_terms: List[str]


class TranslationService:
    """
    Multi-language translation service for medical content.
    
    Features:
    - Medical term preservation (English medical vocabulary)
    - Code-mixing support (natural Indian doctor communication)
    - Script transliteration
    - Language detection
    """
    
    # Language names in their native scripts
    LANGUAGE_NAMES = {
        Language.ENGLISH: "English",
        Language.HINDI: "Hindi (हिंदी)",
        Language.TAMIL: "Tamil (தமிழ்)",
        Language.TELUGU: "Telugu (తెలుగు)",
        Language.BENGALI: "Bengali (বাংলা)",
        Language.MARATHI: "Marathi (मराठी)",
        Language.GUJARATI: "Gujarati (ગુજરાતી)",
        Language.KANNADA: "Kannada (ಕನ್ನಡ)",
        Language.MALAYALAM: "Malayalam (മലയാളം)",
        Language.PUNJABI: "Punjabi (ਪੰਜਾਬੀ)",
        Language.ODIA: "Odia (ଓଡ଼ିଆ)",
        Language.ASSAMESE: "Assamese (অসমীয়া)",
        Language.URDU: "Urdu (اردو)"
    }
    
    # Medical terms to always preserve in English
    MEDICAL_TERMS_PRESERVE = [
        # Scores and systems
        "NEWS2", "qSOFA", "SOFA", "APACHE", "MEWS", "GCS",
        # Conditions
        "Sepsis", "Pneumonia", "COPD", "MI", "CVA", "DKA", "ACS",
        "ARDS", "Shock", "Anaphylaxis", "Asthma", "PE", "DVT",
        # Departments
        "ICU", "CCU", "NICU", "PICU", "OPD", "ER", "OT",
        # Procedures
        "Intubation", "Ventilation", "CPR", "ACLS", "BLS",
        # Measurements
        "HR", "BP", "RR", "SpO2", "SBP", "DBP", "ECG", "CT", "MRI",
        # Medications
        "Ceftriaxone", "Paracetamol", "Amoxicillin", "Insulin",
        "Adrenaline", "Dopamine", "Noradrenaline", "Atropine"
    ]
    
    # Common medical translations (Hindi)
    HINDI_MEDICAL_TERMS = {
        "fever": "बुखार (bukhar)",
        "blood pressure": "रक्तचाप (raktachāp)",
        "heart rate": "हृदय गति (hṛday gati)",
        "breathing": "श्वसन (śvasan)",
        "temperature": "तापमान (tāpmān)",
        "oxygen": "ऑक्सीजन (oxygen)",
        "pulse": "नाड़ी (nāḍī)",
        "patient": "मरीज (marīz) / रोगी (rogī)",
        "doctor": "डॉक्टर (doctor) / चिकित्सक (chikitsak)",
        "hospital": "अस्पताल (aspatāl)",
        "medicine": "दवा (davā)",
        "treatment": "उपचार (upchār)",
        "diagnosis": "निदान (nidān)",
        "symptoms": "लक्षण (lakṣaṇ)",
        "alert": "अलर्ट (alert) / चेतावनी (chetāvanī)",
        "urgent": "तत्काल (tatkāl) / अत्यावश्यक (atyāvaśyak)",
        "review": "समीक्षा (samīkṣā)",
        "monitor": "निगरानी (nigarānī)"
    }
    
    def __init__(
        self,
        default_language: Language = Language.ENGLISH,
        preserve_medical_terms: bool = True
    ):
        """
        Initialize translation service.
        
        Args:
            default_language: Default language for translations
            preserve_medical_terms: Keep English medical terms in translations
        """
        self.default_language = default_language
        self.preserve_medical_terms = preserve_medical_terms
        
        # In production, would initialize actual translation models
        # For now, using dictionaries for demonstration
        logger.info(f"Translation service initialized. Default: {default_language}")
    
    def translate(
        self,
        text: str,
        target_lang: Language,
        source_lang: Optional[Language] = None,
        preserve_terms: bool = True
    ) -> TranslationResult:
        """
        Translate medical text to target language.
        
        Args:
            text: Text to translate
            target_lang: Target language
            source_lang: Source language (auto-detect if None)
            preserve_terms: Preserve English medical terms
        
        Returns:
            TranslationResult with translated text
        """
        # Detect source language if not provided
        if source_lang is None:
            source_lang = self.detect_language(text)
        
        # If source and target are same, return as-is
        if source_lang == target_lang:
            return TranslationResult(
                translated_text=text,
                source_lang=source_lang,
                target_lang=target_lang,
                confidence=1.0,
                preserved_terms=[]
            )
        
        # Extract and preserve medical terms
        preserved_terms = []
        if preserve_terms:
            preserved_terms = self._extract_medical_terms(text)
        
        # Translate
        # In production, would use actual translation model/API
        translated = self._mock_translate(text, source_lang, target_lang, preserved_terms)
        
        return TranslationResult(
            translated_text=translated,
            source_lang=source_lang,
            target_lang=target_lang,
            confidence=0.85,  # Would be actual confidence from model
            preserved_terms=preserved_terms
        )
    
    def detect_language(self, text: str) -> Language:
        """
        Detect language of input text.
        
        Args:
            text: Input text
        
        Returns:
            Detected language
        """
        # In production, would use fastText or similar
        # Simple heuristic for demo
        if any(ord(char) in range(0x0900, 0x097F) for char in text):
            return Language.HINDI
        elif any(ord(char) in range(0x0B80, 0x0BFF) for char in text):
            return Language.TAMIL
        elif any(ord(char) in range(0x0C00, 0x0C7F) for char in text):
            return Language.TELUGU
        elif any(ord(char) in range(0x0980, 0x09FF) for char in text):
            return Language.BENGALI
        else:
            return Language.ENGLISH
    
    def transliterate(
        self,
        text: str,
        from_script: str,
        to_script: str
    ) -> str:
        """
        Transliterate text between scripts.
        
        Examples:
        - Latin to Devanagari: "sepsis" → "सेप्सिस"
        - Devanagari to Latin: "बुखार" → "bukhar"
        
        Args:
            text: Text to transliterate
            from_script: Source script
            to_script: Target script
        
        Returns:
            Transliterated text
        """
        # In production, would use Aksharamukha or similar
        logger.info(f"Transliterating from {from_script} to {to_script}")
        return text  # Mock implementation
    
    def get_medical_glossary(
        self,
        language: Language
    ) -> Dict[str, str]:
        """
        Get medical terminology glossary for language.
        
        Args:
            language: Target language
        
        Returns:
            Dictionary of English term → translated term
        """
        if language == Language.HINDI:
            return self.HINDI_MEDICAL_TERMS
        
        # In production, would have glossaries for all languages
        return {}
    
    def translate_vitals(
        self,
        vitals: Dict,
        target_lang: Language
    ) -> Dict:
        """
        Translate vital signs labels to target language.
        
        Args:
            vitals: Dictionary of vital signs
            target_lang: Target language
        
        Returns:
            Dictionary with translated labels
        """
        if target_lang == Language.ENGLISH:
            return vitals
        
        # Translate labels
        label_translations = self._get_vital_labels(target_lang)
        
        translated = {}
        for key, value in vitals.items():
            translated_key = label_translations.get(key, key)
            translated[translated_key] = value
        
        return translated
    
    def create_bilingual_prompt(
        self,
        instruction_en: str,
        input_en: str,
        language: Language
    ) -> str:
        """
        Create bilingual prompt for LLM (English + target language).
        
        Args:
            instruction_en: Instruction in English
            input_en: Input in English
            language: Target language
        
        Returns:
            Bilingual prompt
        """
        if language == Language.ENGLISH:
            return f"""### Instruction:
{instruction_en}

### Input:
{input_en}

### Response:
"""
        
        # Translate instruction and input
        instruction_translated = self.translate(instruction_en, language).translated_text
        input_translated = self.translate(input_en, language).translated_text
        
        # Create bilingual prompt
        return f"""### निर्देश (Instruction):
{instruction_translated}

### इनपुट (Input):
{input_translated}

### उत्तर (Response):
"""
    
    # Internal methods
    
    def _extract_medical_terms(self, text: str) -> List[str]:
        """Extract medical terms from text to preserve."""
        preserved = []
        text_upper = text.upper()
        
        for term in self.MEDICAL_TERMS_PRESERVE:
            if term.upper() in text_upper:
                preserved.append(term)
        
        return preserved
    
    def _mock_translate(
        self,
        text: str,
        source_lang: Language,
        target_lang: Language,
        preserved_terms: List[str]
    ) -> str:
        """
        Mock translation for demonstration.
        
        In production, would use:
        - Google Translate API (Indian languages)
        - Microsoft Azure Translator
        - IndicTrans (AI4Bharat)
        - Custom fine-tuned models
        """
        if target_lang == Language.HINDI:
            # Simple Hindi translation examples
            translations = {
                "Patient has high fever": "मरीज को तेज बुखार है",
                "Blood pressure is low": "रक्तचाप कम है",
                "Heart rate is elevated": "हृदय गति बढ़ी हुई है",
                "Urgent clinical review required": "तत्काल नैदानिक समीक्षा आवश्यक है",
                "Monitor vital signs": "वाइटल साइन्स की निगरानी करें"
            }
            
            # Try exact match
            if text in translations:
                result = translations[text]
            else:
                # Mock translation
                result = f"[हिंदी अनुवाद: {text}]"
            
            # Re-insert preserved terms
            for term in preserved_terms:
                result = result.replace(f"[{term}]", term)
            
            return result
        
        return f"[Translation to {target_lang}: {text}]"
    
    def _get_vital_labels(self, language: Language) -> Dict[str, str]:
        """Get vital sign labels in target language."""
        if language == Language.HINDI:
            return {
                "hr": "हृदय गति (HR)",
                "bp": "रक्तचाप (BP)",
                "sbp": "सिस्टोलिक BP (SBP)",
                "dbp": "डायस्टोलिक BP (DBP)",
                "rr": "श्वसन दर (RR)",
                "temp": "तापमान (Temp)",
                "spo2": "ऑक्सीजन संतृप्ति (SpO2)",
                "consciousness": "चेतना स्तर"
            }
        
        return {}
    
    def get_supported_languages(self) -> List[Dict]:
        """
        Get list of supported languages.
        
        Returns:
            List of language info dictionaries
        """
        return [
            {
                "code": lang.value,
                "name": self.LANGUAGE_NAMES[lang],
                "status": "complete" if lang in [Language.ENGLISH, Language.HINDI] else "in_progress"
            }
            for lang in Language
        ]


# Example usage
if __name__ == "__main__":
    # Initialize service
    translator = TranslationService()
    
    # Get supported languages
    languages = translator.get_supported_languages()
    print("Supported languages:")
    for lang in languages:
        print(f"  {lang['code']}: {lang['name']} ({lang['status']})")
    
    # Translate text
    result = translator.translate(
        text="Patient has high fever and low blood pressure",
        target_lang=Language.HINDI
    )
    print(f"\nTranslation:")
    print(f"  Source ({result.source_lang}): Patient has high fever and low blood pressure")
    print(f"  Target ({result.target_lang}): {result.translated_text}")
    print(f"  Preserved terms: {result.preserved_terms}")
    
    # Detect language
    hindi_text = "मरीज को तेज बुखार है"
    detected = translator.detect_language(hindi_text)
    print(f"\nLanguage detection:")
    print(f"  Text: {hindi_text}")
    print(f"  Detected: {detected}")
    
    # Bilingual prompt
    prompt = translator.create_bilingual_prompt(
        instruction_en="Explain the NEWS2 score",
        input_en="NEWS2 score is 8",
        language=Language.HINDI
    )
    print(f"\nBilingual prompt:")
    print(prompt)
