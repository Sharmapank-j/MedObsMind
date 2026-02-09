package com.medobsmind.app;

import android.Manifest;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.speech.tts.TextToSpeech;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class ChatActivity extends AppCompatActivity {
    private RecyclerView chatRecyclerView;
    private ChatAdapter chatAdapter;
    private EditText messageInput;
    private Button sendButton, voiceButton, videoButton;
    private List<ChatMessage> messages;
    private String selectedModel;
    
    private SpeechRecognizer speechRecognizer;
    private TextToSpeech textToSpeech;
    private boolean isListening = false;
    
    private static final String PREFS_NAME = "MedObsMindPrefs";
    private static final String PREF_MODEL = "selected_model";
    private static final int REQUEST_RECORD_AUDIO_PERMISSION = 200;
    private static final int REQUEST_CAMERA_PERMISSION = 201;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat);

        // Initialize UI components
        chatRecyclerView = findViewById(R.id.chatRecyclerView);
        messageInput = findViewById(R.id.messageInput);
        sendButton = findViewById(R.id.sendButton);
        voiceButton = findViewById(R.id.voiceButton);
        videoButton = findViewById(R.id.videoButton);

        // Setup RecyclerView
        messages = new ArrayList<>();
        chatAdapter = new ChatAdapter(messages);
        chatRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        chatRecyclerView.setAdapter(chatAdapter);

        // Load selected model
        loadSelectedModel();

        // Initialize Speech Recognition
        initializeSpeechRecognizer();
        
        // Initialize Text-to-Speech
        initializeTextToSpeech();

        // Add welcome message
        addWelcomeMessage();

        // Setup send button click listener
        sendButton.setOnClickListener(v -> sendMessage());
        
        // Setup voice button click listener
        voiceButton.setOnClickListener(v -> toggleVoiceInput());
        
        // Setup video button click listener
        videoButton.setOnClickListener(v -> startVideoCall());
    }

    @Override
    protected void onResume() {
        super.onResume();
        loadSelectedModel();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (speechRecognizer != null) {
            speechRecognizer.destroy();
        }
        if (textToSpeech != null) {
            textToSpeech.stop();
            textToSpeech.shutdown();
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.chat_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        if (item.getItemId() == R.id.action_settings) {
            Intent intent = new Intent(this, SettingsActivity.class);
            startActivity(intent);
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    private void loadSelectedModel() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        selectedModel = prefs.getString(PREF_MODEL, "GPT-4");
        setTitle(getString(R.string.chat_title) + " (" + selectedModel + ")");
    }

    private void addWelcomeMessage() {
        if (messages.isEmpty()) {
            ChatMessage welcomeMsg = new ChatMessage(
                getString(R.string.welcome_message),
                false
            );
            messages.add(welcomeMsg);
            chatAdapter.notifyItemInserted(messages.size() - 1);
        }
    }

    private void sendMessage() {
        String messageText = messageInput.getText().toString().trim();
        
        if (messageText.isEmpty()) {
            Toast.makeText(this, R.string.error_empty_message, Toast.LENGTH_SHORT).show();
            return;
        }

        // Add user message
        ChatMessage userMessage = new ChatMessage(messageText, true);
        messages.add(userMessage);
        chatAdapter.notifyItemInserted(messages.size() - 1);
        chatRecyclerView.scrollToPosition(messages.size() - 1);

        // Clear input
        messageInput.setText("");

        // Simulate AI response (in a real app, this would call an API)
        simulateAIResponse(messageText);
    }

    private void simulateAIResponse(String userMessage) {
        // This is a placeholder. In a real app, you would:
        // 1. Send the message to your AI API with the selected model
        // 2. Get the response
        // 3. Display it in the chat
        
        String systemPrompt = getString(R.string.system_prompt);
        String response = "This is a simulated response from " + selectedModel + 
            ". In a production app, this would connect to the actual AI model API.\n\n" +
            "Your message: \"" + userMessage + "\"\n\n" +
            "System Prompt: " + systemPrompt;

        ChatMessage aiMessage = new ChatMessage(response, false);
        messages.add(aiMessage);
        chatAdapter.notifyItemInserted(messages.size() - 1);
        chatRecyclerView.scrollToPosition(messages.size() - 1);
        
        // Speak the AI response
        speakText(response);
    }
    
    private void initializeSpeechRecognizer() {
        if (SpeechRecognizer.isRecognitionAvailable(this)) {
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this);
            speechRecognizer.setRecognitionListener(new RecognitionListener() {
                @Override
                public void onReadyForSpeech(Bundle params) {
                    voiceButton.setText(R.string.listening);
                }

                @Override
                public void onBeginningOfSpeech() {}

                @Override
                public void onRmsChanged(float rmsdB) {}

                @Override
                public void onBufferReceived(byte[] buffer) {}

                @Override
                public void onEndOfSpeech() {
                    isListening = false;
                    voiceButton.setText(R.string.voice_input_button);
                }

                @Override
                public void onError(int error) {
                    isListening = false;
                    voiceButton.setText(R.string.voice_input_button);
                    Toast.makeText(ChatActivity.this, R.string.error_speech_recognition, Toast.LENGTH_SHORT).show();
                }

                @Override
                public void onResults(Bundle results) {
                    isListening = false;
                    voiceButton.setText(R.string.voice_input_button);
                    ArrayList<String> matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
                    if (matches != null && !matches.isEmpty()) {
                        messageInput.setText(matches.get(0));
                        sendMessage();
                    }
                }

                @Override
                public void onPartialResults(Bundle partialResults) {}

                @Override
                public void onEvent(int eventType, Bundle params) {}
            });
        }
    }
    
    private void initializeTextToSpeech() {
        textToSpeech = new TextToSpeech(this, status -> {
            if (status == TextToSpeech.SUCCESS) {
                int result = textToSpeech.setLanguage(Locale.US);
                if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    Toast.makeText(this, "Text-to-speech language not supported", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }
    
    private void toggleVoiceInput() {
        if (isListening) {
            stopListening();
        } else {
            startListening();
        }
    }
    
    private void startListening() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) 
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, 
                new String[]{Manifest.permission.RECORD_AUDIO}, 
                REQUEST_RECORD_AUDIO_PERMISSION);
            return;
        }
        
        if (speechRecognizer != null) {
            Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault());
            intent.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true);
            
            isListening = true;
            voiceButton.setText(R.string.stop_recording);
            speechRecognizer.startListening(intent);
        } else {
            Toast.makeText(this, R.string.error_speech_recognition, Toast.LENGTH_SHORT).show();
        }
    }
    
    private void stopListening() {
        if (speechRecognizer != null) {
            speechRecognizer.stopListening();
        }
        isListening = false;
        voiceButton.setText(R.string.voice_input_button);
    }
    
    private void startVideoCall() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) 
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, 
                new String[]{Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO}, 
                REQUEST_CAMERA_PERMISSION);
            return;
        }
        
        Intent intent = new Intent(this, VideoCallActivity.class);
        intent.putExtra("selected_model", selectedModel);
        startActivity(intent);
    }
    
    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        
        if (requestCode == REQUEST_RECORD_AUDIO_PERMISSION) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                startListening();
            } else {
                Toast.makeText(this, R.string.error_microphone_permission, Toast.LENGTH_SHORT).show();
            }
        } else if (requestCode == REQUEST_CAMERA_PERMISSION) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                startVideoCall();
            } else {
                Toast.makeText(this, R.string.error_camera_permission, Toast.LENGTH_SHORT).show();
            }
        }
    }
    
    private void speakText(String text) {
        if (textToSpeech != null) {
            textToSpeech.speak(text, TextToSpeech.QUEUE_FLUSH, null, null);
        }
    }
}
