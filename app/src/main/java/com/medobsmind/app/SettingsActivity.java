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
    private RadioButton radioMaxAccuracy, radioBalanced, radioFastResponse, radioDetailedAnalysis, radioStandard;
    private Button saveButton;
    
    private static final String PREFS_NAME = "MedObsMindPrefs";
    private static final String PREF_MODEL = "selected_model";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        // Initialize UI components
        modelSelectionGroup = findViewById(R.id.modelSelectionGroup);
        radioMaxAccuracy = findViewById(R.id.radioGpt4);
        radioBalanced = findViewById(R.id.radioGpt35);
        radioFastResponse = findViewById(R.id.radioClaude);
        radioDetailedAnalysis = findViewById(R.id.radioPalm);
        radioStandard = findViewById(R.id.radioLlama);
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
        String savedModel = prefs.getString(PREF_MODEL, "Balanced");

        switch (savedModel) {
            case "Maximum Accuracy":
                radioMaxAccuracy.setChecked(true);
                break;
            case "Balanced":
                radioBalanced.setChecked(true);
                break;
            case "Fast Response":
                radioFastResponse.setChecked(true);
                break;
            case "Detailed Analysis":
                radioDetailedAnalysis.setChecked(true);
                break;
            case "Standard":
                radioStandard.setChecked(true);
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
            selectedModel = "Maximum Accuracy";
        } else if (selectedId == R.id.radioGpt35) {
            selectedModel = "Balanced";
        } else if (selectedId == R.id.radioClaude) {
            selectedModel = "Fast Response";
        } else if (selectedId == R.id.radioPalm) {
            selectedModel = "Detailed Analysis";
        } else if (selectedId == R.id.radioLlama) {
            selectedModel = "Standard";
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
