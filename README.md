# MedObsMind
A professional ai assistant with ai aggregator model for medical informatics 

## Features

### 1. Text-Based Chat
- Interactive chat interface for medical consultations
- Support for multiple AI models (GPT-4, GPT-3.5, Claude, PaLM 2, LLaMA)
- System prompts optimized for medical informatics
- Real-time message display with user and AI differentiation

### 2. Voice Live Chat
- **Speech-to-Text**: Speak your medical questions directly
- **Text-to-Speech**: AI responses are spoken back to you
- Hands-free operation for medical professionals
- Real-time voice recognition

### 3. Live Video Interpretation
- Real-time video analysis for medical contexts
- Camera integration for visual medical information
- AI-powered interpretation of visual data
- Toggle between front and rear cameras
- Mute/unmute controls

### 4. Model Settings
- Easy switching between different AI models
- Persistent settings storage
- Model selection:
  - **GPT-4**: Most accurate for complex medical queries
  - **GPT-3.5**: Faster response times
  - **Claude**: Detailed medical analysis
  - **PaLM 2**: Balanced performance
  - **LLaMA**: Open-source option

## Permissions Required
- `INTERNET`: For AI API communication
- `RECORD_AUDIO`: For voice input/output
- `CAMERA`: For video interpretation
- `MODIFY_AUDIO_SETTINGS`: For audio control

## Usage

1. **Start Chat**: Launch the app to begin text-based chat
2. **Voice Input**: Tap the microphone button to speak your question
3. **Video Consultation**: Tap the video button to start live video interpretation
4. **Change Model**: Access settings menu to select your preferred AI model

## Technical Architecture

- **Android SDK**: Min SDK 24, Target SDK 34
- **UI Framework**: Material Design Components
- **Speech**: Android SpeechRecognizer and TextToSpeech APIs
- **Camera**: Camera2 API for live video
- **Storage**: SharedPreferences for settings persistence
