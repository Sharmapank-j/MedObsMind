package com.medobsmind.app;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.widget.Button;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

public class SettingsActivity extends AppCompatActivity {
    private RadioGroup modelSelectionGroup;
    private RadioButton radioGpt4, radioGpt35, radioClaude, radioPalm, radioLlama;
    private Button saveButton;
    
    private static final String PREFS_NAME = "MedObsMindPrefs";
    private static final String PREF_MODEL = "selected_model";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        // Initialize UI components
        modelSelectionGroup = findViewById(R.id.modelSelectionGroup);
        radioGpt4 = findViewById(R.id.radioGpt4);
        radioGpt35 = findViewById(R.id.radioGpt35);
        radioClaude = findViewById(R.id.radioClaude);
        radioPalm = findViewById(R.id.radioPalm);
        radioLlama = findViewById(R.id.radioLlama);
        saveButton = findViewById(R.id.saveButton);

        // Load saved model
        loadSavedModel();

        // Setup save button
        saveButton.setOnClickListener(v -> saveSettings());

        // Enable back button
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }
    }

    private void loadSavedModel() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        String savedModel = prefs.getString(PREF_MODEL, "GPT-4");

        switch (savedModel) {
            case "GPT-4":
                radioGpt4.setChecked(true);
                break;
            case "GPT-3.5":
                radioGpt35.setChecked(true);
                break;
            case "Claude":
                radioClaude.setChecked(true);
                break;
            case "PaLM 2":
                radioPalm.setChecked(true);
                break;
            case "LLaMA":
                radioLlama.setChecked(true);
                break;
        }
    }

    private void saveSettings() {
        int selectedId = modelSelectionGroup.getCheckedRadioButtonId();
        
        if (selectedId == -1) {
            Toast.makeText(this, R.string.error_model_selection, Toast.LENGTH_SHORT).show();
            return;
        }

        String selectedModel = "";
        if (selectedId == R.id.radioGpt4) {
            selectedModel = "GPT-4";
        } else if (selectedId == R.id.radioGpt35) {
            selectedModel = "GPT-3.5";
        } else if (selectedId == R.id.radioClaude) {
            selectedModel = "Claude";
        } else if (selectedId == R.id.radioPalm) {
            selectedModel = "PaLM 2";
        } else if (selectedId == R.id.radioLlama) {
            selectedModel = "LLaMA";
        }

        // Save to SharedPreferences
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        SharedPreferences.Editor editor = prefs.edit();
        editor.putString(PREF_MODEL, selectedModel);
        editor.apply();

        Toast.makeText(this, R.string.settings_saved, Toast.LENGTH_SHORT).show();
        finish();
    }

    @Override
    public boolean onSupportNavigateUp() {
        finish();
        return true;
    }
}
