# Dsquare Med-assist - Implementation Documentation

## Overview
Dsquare Med-assist is an Android application platform that provides access to **MedObsMind LLMM** (Large Language Medical Model), a specialized AI model for medical informatics. The platform offers text chat, voice interaction, and live video interpretation capabilities powered by the MedObsMind medical language model.

## Architecture

### Activities
1. **ChatActivity** (Main/Launcher)
   - Primary interface for text and voice-based medical consultations
   - Implements RecyclerView for chat history
   - Integrates SpeechRecognizer for voice input
   - Integrates TextToSpeech for voice output
   - Navigation to Settings and Video Call

2. **SettingsActivity**
   - MedObsMind LLMM performance mode selection interface
   - Persistent storage using SharedPreferences
   - Available modes: Maximum Accuracy, Balanced, Fast Response, Detailed Analysis, Standard

3. **VideoCallActivity**
   - Live video streaming with Camera2 API
   - Real-time AI interpretation simulation
   - Camera switching (front/rear)
   - Audio controls (mute/unmute)

### Data Models
- **ChatMessage**: Simple POJO for chat messages
  - `String message`: The message content
  - `boolean isUser`: True for user messages, false for AI responses

### Adapters
- **ChatAdapter**: RecyclerView adapter with two view types
  - `VIEW_TYPE_USER`: Right-aligned blue bubbles
  - `VIEW_TYPE_AI`: Left-aligned white bubbles

## Key Features Implementation

### 1. Text Chat with System Prompts
- **Location**: `ChatActivity.java`, `strings.xml`
- **System Prompt**: Defined in `strings.xml` as `system_prompt`
- Instructs MedObsMind LLMM to act as a specialized medical informatics assistant
- Reminds users to consult healthcare professionals
- Welcome message introduces MedObsMind as an LLMM with its capabilities

### 2. Voice Live Chat
- **Speech-to-Text**: 
  - Uses Android `SpeechRecognizer` API
  - Converts voice to text and auto-sends as message
  - Real-time feedback with button state changes
  
- **Text-to-Speech**:
  - Uses Android `TextToSpeech` API
  - Reads AI responses aloud automatically
  - Configurable language (default: US English)

### 3. Live Video Interpretation
- **Camera Access**: Camera2 API for modern camera control
- **Preview**: TextureView for camera preview
- **Background Processing**: HandlerThread for camera operations
- **LLMM Interpretation**: Placeholder for real MedObsMind LLMM video analysis
- **Controls**: 
  - Camera toggle (front/rear)
  - Mute/unmute
  - End call

## Permissions

### Required Permissions (AndroidManifest.xml)
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
```

### Runtime Permission Handling
- Audio: Requested when voice button is pressed
- Camera: Requested when video button is pressed
- User-friendly error messages for denied permissions

## UI/UX Design

### Material Design Components
- CardView for message bubbles and status overlays
- ConstraintLayout for flexible layouts
- Material color scheme (blue primary)
- RecyclerView for efficient message list

### Responsive Design
- Max-width constraints on message bubbles (280dp)
- Scrollable chat history
- Multi-line text input (up to 4 lines)
- Elevation and shadows for depth

## Data Persistence

### SharedPreferences
- **File**: "MedObsMindPrefs"
- **Keys**:
  - `selected_model`: Stores the currently selected MedObsMind LLMM performance mode
- Persists across app restarts
- Updated in SettingsActivity
- Read in ChatActivity and VideoCallActivity

## Integration Points (For Production)

### MedObsMind LLMM API Integration
The current implementation uses placeholder responses. To integrate the real MedObsMind LLMM:

1. **ChatActivity.simulateAIResponse()**
   - Replace with actual API calls to MedObsMind LLMM backend
   - Send user message + system prompt + selected performance mode
   - Handle async responses from the Large Language Medical Model
   - Consider streaming responses for better UX

2. **VideoCallActivity.simulateAIInterpretation()**
   - Capture video frames from camera
   - Send frames to MedObsMind LLMM vision API
   - Display real-time interpretations from the medical model
   - Handle video processing latency

### Recommended Libraries
- **Retrofit/OkHttp**: For API communication
- **Gson/Moshi**: For JSON parsing
- **Coroutines/RxJava**: For async operations
- **WebRTC**: For real-time video streaming (if needed)

## Testing Considerations

### Unit Tests
- ChatMessage model validation
- SharedPreferences operations
- Message list management

### UI Tests (Espresso)
- Chat message sending flow
- Settings persistence
- Permission request flows
- Voice/Video button interactions

### Integration Tests
- Voice recognition flow
- Text-to-speech flow
- Camera preview lifecycle

## Security Considerations

1. **API Keys**: Store securely (use BuildConfig or secure storage)
2. **HTTPS**: Always use encrypted connections
3. **Data Privacy**: 
   - Consider HIPAA compliance for medical data
   - Encrypt sensitive information
   - Clear chat history option
4. **Permissions**: Request only when needed (runtime permissions)

## Build Configuration

### Minimum Requirements
- minSdk: 24 (Android 7.0)
- targetSdk: 34 (Android 14)
- Compile SDK: 34

### Dependencies
- androidx.appcompat
- com.google.android.material
- androidx.constraintlayout
- androidx.recyclerview

## Future Enhancements

1. **Chat History Persistence**: Save conversations to database
2. **Multi-language Support**: Localization for international users
3. **Offline Mode**: Cache responses and work without internet
4. **File Attachments**: Share medical images/documents
5. **Real AI Integration**: Connect to actual AI APIs
6. **Voice Commands**: Advanced voice control features
7. **Video Recording**: Record consultation sessions
8. **Medical Disclaimer**: Legal disclaimer dialog
9. **User Authentication**: Secure login system
10. **Analytics**: Usage tracking and improvement insights

## Troubleshooting

### Common Issues

1. **Speech Recognition Not Working**
   - Ensure RECORD_AUDIO permission granted
   - Check device has speech recognition capability
   - Verify Google app is updated

2. **Camera Preview Black Screen**
   - Verify CAMERA permission granted
   - Check camera is not used by another app
   - Ensure proper Camera2 API support

3. **Text-to-Speech Not Speaking**
   - Check TTS data is downloaded
   - Verify device audio is not muted
   - Check TTS engine is available

## Contributing

When contributing to this project:
1. Follow Android coding conventions
2. Add comments for complex logic
3. Update documentation for new features
4. Test on multiple Android versions
5. Ensure accessibility compliance

## License

[Specify your license here]

## Contact

[Your contact information]
