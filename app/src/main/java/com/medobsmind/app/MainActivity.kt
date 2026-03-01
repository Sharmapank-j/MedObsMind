package com.medobsmind.app

import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import com.medobsmind.app.databinding.ActivityMainBinding
import com.medobsmind.app.viewmodel.MedicalAIViewModel
import timber.log.Timber

/**
 * MainActivity - Entry point for MedObsMind Android application
 * 
 * This activity hosts the main UI for the on-device medical AI assistant.
 * It provides access to:
 * - Medical query interface
 * - AI camera assistance
 * - Educational simulations
 * - Offline medical knowledge base
 */
class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: MedicalAIViewModel
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize ViewBinding
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // Initialize ViewModel
        viewModel = ViewModelProvider(this)[MedicalAIViewModel::class.java]
        
        // Setup UI
        setupUI()
        
        // Observe ViewModel
        observeViewModel()
        
        // Initialize on-device AI model
        initializeAIModel()
        
        Timber.d("MainActivity created")
    }
    
    private fun setupUI() {
        // Setup toolbar
        setSupportActionBar(binding.toolbar)
        
        // Setup bottom navigation or main UI elements
        binding.apply {
            // TODO: Setup navigation components
            // TODO: Setup query input
            // TODO: Setup camera button
            // TODO: Setup educational modules button
        }
    }
    
    private fun observeViewModel() {
        // Observe AI model loading status
        viewModel.modelLoadingStatus.observe(this) { status ->
            when (status) {
                is ModelStatus.Loading -> showLoading()
                is ModelStatus.Loaded -> hideLoading()
                is ModelStatus.Error -> showError(status.message)
            }
        }
        
        // Observe AI responses
        viewModel.aiResponse.observe(this) { response ->
            displayResponse(response)
        }
    }
    
    private fun initializeAIModel() {
        // Initialize TensorFlow Lite model or ONNX Runtime
        viewModel.initializeModel(applicationContext)
    }
    
    private fun showLoading() {
        binding.progressBar.visibility = View.VISIBLE
    }
    
    private fun hideLoading() {
        binding.progressBar.visibility = View.GONE
    }
    
    private fun showError(message: String) {
        Timber.e("Error: $message")
        // TODO: Show error dialog or snackbar
    }
    
    private fun displayResponse(response: String) {
        // TODO: Display AI response in UI
        Timber.d("AI Response: $response")
    }
    
    override fun onDestroy() {
        super.onDestroy()
        // Clean up resources
        viewModel.cleanup()
    }
}

/**
 * Sealed class for model loading status
 */
sealed class ModelStatus {
    object Loading : ModelStatus()
    object Loaded : ModelStatus()
    data class Error(val message: String) : ModelStatus()
}
