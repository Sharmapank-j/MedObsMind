package com.medobsmind.app;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;
import java.util.List;

public class ChatActivity extends AppCompatActivity {
    private RecyclerView chatRecyclerView;
    private ChatAdapter chatAdapter;
    private EditText messageInput;
    private Button sendButton;
    private List<ChatMessage> messages;
    private String selectedModel;
    
    private static final String PREFS_NAME = "MedObsMindPrefs";
    private static final String PREF_MODEL = "selected_model";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat);

        // Initialize UI components
        chatRecyclerView = findViewById(R.id.chatRecyclerView);
        messageInput = findViewById(R.id.messageInput);
        sendButton = findViewById(R.id.sendButton);

        // Setup RecyclerView
        messages = new ArrayList<>();
        chatAdapter = new ChatAdapter(messages);
        chatRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        chatRecyclerView.setAdapter(chatAdapter);

        // Load selected model
        loadSelectedModel();

        // Add welcome message
        addWelcomeMessage();

        // Setup send button click listener
        sendButton.setOnClickListener(v -> sendMessage());
    }

    @Override
    protected void onResume() {
        super.onResume();
        loadSelectedModel();
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
    }
}
