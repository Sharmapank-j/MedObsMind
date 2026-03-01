# Dsquare Med-assist - Prompts and System Messages

This document describes the prompts and system messages used in Dsquare Med-assist platform to interact with **MedObsMind LLMM** (Large Language Medical Model).

## System Prompt

The core system prompt that defines MedObsMind LLMM's behavior:

```
You are MedObsMind, a Large Language Medical Model (LLMM) and the AI agent of 
Dsquare Med-assist platform. You are specialized in medical informatics and healthcare. 
Provide accurate, evidence-based medical information while being clear that users should 
consult healthcare professionals for medical advice. You have capabilities in text, voice, 
and video interpretation.
```

**Purpose**: 
- Establishes MedObsMind LLMM's role as a specialized medical model
- Sets expectations for medical information accuracy
- Includes important disclaimer about consulting professionals
- Highlights multi-modal capabilities (text, voice, video)

**Usage**: 
- Sent with every user query to the MedObsMind LLMM
- Ensures consistent behavior across conversations
- Can be customized per performance mode in settings

---

## Welcome Message

The initial greeting shown when users open the chat:

```
Welcome to Dsquare Med-assist!

I'm MedObsMind, a Large Language Medical Model (LLMM) specialized in medical 
informatics. I can help you with:

• Medical research questions
• Clinical decision support
• Drug information
• Medical terminology
• Healthcare data analysis
• Image and video interpretation

How can I assist you today?
```

**Purpose**:
- Introduces the platform (Dsquare Med-assist) and the LLMM (MedObsMind)
- Explains that MedObsMind is a Large Language Medical Model
- Sets user expectations about capabilities
- Encourages engagement

---

## User Interface Prompts

### Chat Input Placeholder
```
Ask MedObsMind (LLMM) anything about medical informatics…
```

**Purpose**: Guides users on what type of questions to ask the Large Language Medical Model

### Voice Input Feedback
- **Ready**: "Voice Input"
- **Listening**: "Listening..."
- **Processing**: "Processing speech..."
- **Speaking**: "Speaking..."
- **Stop**: "Stop"

**Purpose**: Provides clear feedback on voice interaction status

### Video Interpretation Status
```
MedObsMind LLMM is analyzing video… - Using [Performance Mode]
```

**Purpose**: Informs user that MedObsMind video analysis is active

---

## MedObsMind LLMM Performance Mode Prompts

Each performance mode has a descriptive prompt to help users choose:

### Maximum Accuracy Mode
```
Maximum Accuracy Mode
```
**Use Case**: Complex medical queries requiring highest accuracy from the LLMM

### Balanced Mode
```
Balanced Mode (Recommended)
```
**Use Case**: General medical informatics questions (default configuration)

### Fast Response Mode
```
Fast Response Mode
```
**Use Case**: Quick consultations where speed is preferred

### Detailed Analysis Mode
```
Detailed Analysis Mode
```
**Use Case**: In-depth medical analysis and detailed explanations

### Standard Mode
```
Standard Mode
```
**Use Case**: Standard medical assistance queries

---

## Settings Prompts

### Configuration Title
```
MedObsMind LLMM Configuration
```

### Configuration Description
```
Configure MedObsMind (Large Language Medical Model) performance and behavior
```

**Purpose**: Clearly explains that settings control the Large Language Medical Model's behavior

---

## Error Messages

### Empty Message Error
```
Please enter a message
```
**Trigger**: User tries to send empty text

### Model Selection Error
```
Please select an AI model
```
**Trigger**: Attempting to save settings without selecting a model

### Permission Errors

#### General Permission Denied
```
Permission denied. Please grant necessary permissions.
```

#### Microphone Permission
```
Microphone permission is required for voice input
```
**Trigger**: Voice button pressed without audio permission

#### Camera Permission
```
Camera permission is required for video calls
```
**Trigger**: Video button pressed without camera permission

#### Speech Recognition Error
```
Speech recognition not available
```
**Trigger**: Device doesn't support speech recognition

---

## Video Call Prompts

### Video Interpretation Description
```
MedObsMind (Large Language Medical Model) live video interpretation analyzes 
visual medical information in real-time
```

### LLMM Interpretation Response (Simulated)
```
MedObsMind LLMM Interpretation ([Performance Mode]):

This is a simulated video interpretation response from MedObsMind 
(Large Language Medical Model).

In a production app, the Dsquare Med-assist platform would:
• Send video frames to MedObsMind LLMM API
• Analyze visual medical information in real-time
• Identify medical instruments or conditions
• Provide contextual medical guidance
• Assist with medical documentation

MedObsMind LLMM is specialized for medical visual interpretation.
```

**Note**: This is a placeholder for demonstration purposes

---

## Button Labels

### Action Buttons
- **Send**: "Send"
- **Voice Input**: "Voice Input"
- **Video Call**: "Video Consultation"
- **Settings**: "Settings"
- **Save**: "Save"

### Video Controls
- **Toggle Camera**: "Switch Camera"
- **Toggle Mic**: "Mute/Unmute"
- **End Call**: "End Call"

---

## Success Messages

### Settings Saved
```
Settings saved successfully
```
**Trigger**: User successfully saves model selection

---

## Customization Guide

### Adding New Prompts

1. **Add to strings.xml**:
```xml
<string name="new_prompt">Your prompt text here</string>
```

2. **Reference in Java**:
```java
String prompt = getString(R.string.new_prompt);
```

3. **Use in layout**:
```xml
android:text="@string/new_prompt"
```

### Modifying System Prompt

To customize the system prompt for specific use cases:

1. Open `app/src/main/res/values/strings.xml`
2. Find `<string name="system_prompt">`
3. Modify the text while keeping the medical disclaimer
4. Consider creating variants for different specialties

**Example Variants**:
- Cardiology focus: Add expertise in heart-related topics
- Pediatrics focus: Add child-specific medical context
- Emergency medicine: Emphasize urgency and critical thinking

### Localization

To add support for other languages:

1. Create `values-[lang]/strings.xml` (e.g., `values-es/`)
2. Translate all string resources
3. System will automatically use appropriate language
4. Consider medical terminology accuracy in translation

---

## Best Practices

### Writing Effective Prompts

1. **Be Clear and Specific**: Use precise medical terminology
2. **Set Boundaries**: Include disclaimers where appropriate
3. **User-Friendly**: Use plain language when possible
4. **Contextual**: Adapt prompts to user's current state
5. **Actionable**: Guide users on what to do next

### Testing Prompts

1. Test with various user inputs
2. Verify AI responses align with system prompt
3. Check prompt clarity with non-technical users
4. Validate medical accuracy with healthcare professionals
5. Test in different languages (if localized)

---

## Compliance Notes

### Medical Disclaimer
All prompts include appropriate disclaimers:
- AI is not a replacement for healthcare professionals
- Users should consult doctors for medical advice
- Information is for educational purposes

### HIPAA Considerations
When deploying in production:
- Never include patient identifiable information in prompts
- Secure all data transmission
- Log prompt usage for audit trails
- Consider prompt sanitization for sensitive data

---

## Prompt Evolution

Track prompt changes over time:

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| 1.0 | 2026-02-09 | Initial prompts | Base implementation |
| Future | TBD | Refinements | Based on user feedback |

---

## Feedback Collection

To improve prompts:
1. Monitor user satisfaction
2. Analyze successful vs. unsuccessful interactions
3. A/B test prompt variations
4. Gather healthcare professional feedback
5. Update based on AI model capabilities
