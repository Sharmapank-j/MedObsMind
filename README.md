# Dsquare Med-assist

A professional medical assistant platform powered by **MedObsMind**, a Large Language Medical Model (LLMM) specialized in medical informatics.

## Overview

**Dsquare Med-assist** is the platform that provides access to **MedObsMind LLMM** - a specialized Large Language Medical Model designed specifically for healthcare and medical informatics applications.

## Features

### 1. Text-Based Chat
- Interactive chat interface for medical consultations powered by MedObsMind LLMM
- Multiple performance modes (Maximum Accuracy, Balanced, Fast Response, Detailed Analysis, Standard)
- System prompts optimized for medical informatics
- Real-time message display with user and LLMM differentiation

### 2. Voice Live Chat
- **Speech-to-Text**: Speak your medical questions directly to MedObsMind
- **Text-to-Speech**: MedObsMind LLMM responses are spoken back to you
- Hands-free operation for medical professionals
- Real-time voice recognition

### 3. Live Video Interpretation
- Real-time video analysis by MedObsMind LLMM for medical contexts
- Camera integration for visual medical information
- LLMM-powered interpretation of visual data
- Toggle between front and rear cameras
- Mute/unmute controls

### 4. MedObsMind LLMM Configuration
- Easy switching between different performance modes
- Persistent settings storage
- Performance modes:
  - **Maximum Accuracy**: Most accurate for complex medical queries
  - **Balanced**: Recommended for general use (default)
  - **Fast Response**: Faster response times
  - **Detailed Analysis**: In-depth medical analysis
  - **Standard**: Standard medical assistance

## Permissions Required
- `INTERNET`: For AI API communication
- `RECORD_AUDIO`: For voice input/output
- `CAMERA`: For video interpretation
- `MODIFY_AUDIO_SETTINGS`: For audio control

## Usage

1. **Start Chat**: Launch Dsquare Med-assist to begin text-based chat with MedObsMind LLMM
2. **Voice Input**: Tap the microphone button to speak your question to MedObsMind
3. **Video Consultation**: Tap the video button to start live video interpretation with MedObsMind LLMM
4. **Configure Settings**: Access settings menu to adjust MedObsMind performance mode

## About MedObsMind LLMM

MedObsMind is a **Large Language Medical Model (LLMM)** - a specialized language model trained and optimized specifically for:
- Medical informatics
- Healthcare applications
- Clinical decision support
- Medical terminology and research
- Visual medical interpretation
- Evidence-based medical information

Unlike general-purpose language models, MedObsMind LLMM is purpose-built for the medical domain, ensuring higher accuracy and relevance for healthcare-related queries.

## Technical Architecture

- **Android SDK**: Min SDK 24, Target SDK 34
- **UI Framework**: Material Design Components
- **Speech**: Android SpeechRecognizer and TextToSpeech APIs
- **Camera**: Camera2 API for live video
- **Storage**: SharedPreferences for settings persistence
