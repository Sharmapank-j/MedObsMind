package com.medobsmind.app;

import android.Manifest;
import android.content.pm.PackageManager;
import android.graphics.SurfaceTexture;
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraCaptureSession;
import android.hardware.camera2.CameraDevice;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.CaptureRequest;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.view.Surface;
import android.view.TextureView;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.cardview.widget.CardView;
import androidx.core.app.ActivityCompat;

import java.util.Arrays;

public class VideoCallActivity extends AppCompatActivity {
    private TextureView cameraPreview;
    private TextView statusText, aiResponseText;
    private CardView aiResponseCard;
    private Button toggleCameraButton, muteButton, endCallButton;
    
    private CameraDevice cameraDevice;
    private CameraCaptureSession cameraCaptureSession;
    private CaptureRequest.Builder captureRequestBuilder;
    private Handler backgroundHandler;
    private HandlerThread backgroundThread;
    
    private boolean isMuted = false;
    private boolean isFrontCamera = true;
    private String selectedModel;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_video_call);
        
        // Get selected model
        selectedModel = getIntent().getStringExtra("selected_model");
        if (selectedModel == null) {
            selectedModel = "Balanced";
        }

        // Initialize UI components
        cameraPreview = findViewById(R.id.cameraPreview);
        statusText = findViewById(R.id.statusText);
        aiResponseText = findViewById(R.id.aiResponseText);
        aiResponseCard = findViewById(R.id.aiResponseCard);
        toggleCameraButton = findViewById(R.id.toggleCameraButton);
        muteButton = findViewById(R.id.muteButton);
        endCallButton = findViewById(R.id.endCallButton);

        // Setup button listeners
        toggleCameraButton.setOnClickListener(v -> toggleCamera());
        muteButton.setOnClickListener(v -> toggleMute());
        endCallButton.setOnClickListener(v -> endCall());

        // Setup camera preview
        cameraPreview.setSurfaceTextureListener(surfaceTextureListener);
        
        // Update status
        statusText.setText(getString(R.string.video_interpreting) + " - Using " + selectedModel);
        
        // Simulate AI interpretation after a delay
        new Handler().postDelayed(this::simulateAIInterpretation, 3000);
    }

    private final TextureView.SurfaceTextureListener surfaceTextureListener = new TextureView.SurfaceTextureListener() {
        @Override
        public void onSurfaceTextureAvailable(SurfaceTexture surface, int width, int height) {
            openCamera();
        }

        @Override
        public void onSurfaceTextureSizeChanged(SurfaceTexture surface, int width, int height) {}

        @Override
        public boolean onSurfaceTextureDestroyed(SurfaceTexture surface) {
            return false;
        }

        @Override
        public void onSurfaceTextureUpdated(SurfaceTexture surface) {}
    };

    private void openCamera() {
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.CAMERA) 
                != PackageManager.PERMISSION_GRANTED) {
            return;
        }

        CameraManager manager = (CameraManager) getSystemService(CAMERA_SERVICE);
        try {
            String[] cameraIdList = manager.getCameraIdList();
            if (cameraIdList.length == 0) {
                Toast.makeText(this, "No camera available", Toast.LENGTH_SHORT).show();
                return;
            }
            
            // Select camera: front camera if available and requested, otherwise use first camera
            String cameraId;
            if (isFrontCamera && cameraIdList.length > 1) {
                cameraId = cameraIdList[1];
            } else {
                cameraId = cameraIdList[0];
            }
            
            manager.openCamera(cameraId, stateCallback, backgroundHandler);
        } catch (CameraAccessException e) {
            e.printStackTrace();
            Toast.makeText(this, "Failed to open camera", Toast.LENGTH_SHORT).show();
        }
    }

    private final CameraDevice.StateCallback stateCallback = new CameraDevice.StateCallback() {
        @Override
        public void onOpened(@NonNull CameraDevice camera) {
            cameraDevice = camera;
            createCameraPreview();
        }

        @Override
        public void onDisconnected(@NonNull CameraDevice camera) {
            cameraDevice.close();
        }

        @Override
        public void onError(@NonNull CameraDevice camera, int error) {
            cameraDevice.close();
            cameraDevice = null;
        }
    };

    private void createCameraPreview() {
        try {
            SurfaceTexture texture = cameraPreview.getSurfaceTexture();
            if (texture == null) return;
            
            texture.setDefaultBufferSize(cameraPreview.getWidth(), cameraPreview.getHeight());
            Surface surface = new Surface(texture);
            
            captureRequestBuilder = cameraDevice.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW);
            captureRequestBuilder.addTarget(surface);
            
            cameraDevice.createCaptureSession(Arrays.asList(surface), new CameraCaptureSession.StateCallback() {
                @Override
                public void onConfigured(@NonNull CameraCaptureSession session) {
                    if (cameraDevice == null) return;
                    
                    cameraCaptureSession = session;
                    captureRequestBuilder.set(CaptureRequest.CONTROL_MODE, CaptureRequest.CONTROL_MODE_AUTO);
                    
                    try {
                        cameraCaptureSession.setRepeatingRequest(captureRequestBuilder.build(), null, backgroundHandler);
                    } catch (CameraAccessException e) {
                        e.printStackTrace();
                    }
                }

                @Override
                public void onConfigureFailed(@NonNull CameraCaptureSession session) {
                    Toast.makeText(VideoCallActivity.this, "Configuration change failed", Toast.LENGTH_SHORT).show();
                }
            }, null);
        } catch (CameraAccessException e) {
            e.printStackTrace();
        }
    }

    private void toggleCamera() {
        if (cameraDevice != null) {
            cameraDevice.close();
            cameraDevice = null;
        }
        isFrontCamera = !isFrontCamera;
        openCamera();
    }

    private void toggleMute() {
        isMuted = !isMuted;
        String message = isMuted ? "Microphone muted" : "Microphone unmuted";
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }

    private void endCall() {
        finish();
    }

    private void simulateAIInterpretation() {
        // In a real app, this would:
        // 1. Capture frames from the camera
        // 2. Send them to the MedObsMind LLMM API for interpretation
        // 3. Display the LLMM's visual analysis
        
        String interpretation = "MedObsMind LLMM Interpretation (" + selectedModel + " mode):\n\n" +
            "This is a simulated video interpretation response from MedObsMind (Large Language Medical Model).\n\n" +
            "In a production app, the Dsquare Med-assist platform would:\n" +
            "• Send video frames to MedObsMind LLMM API\n" +
            "• Analyze visual medical information in real-time\n" +
            "• Identify medical instruments or conditions\n" +
            "• Provide contextual medical guidance\n" +
            "• Assist with medical documentation\n\n" +
            "MedObsMind LLMM is specialized for medical visual interpretation.";
        
        runOnUiThread(() -> {
            aiResponseCard.setVisibility(android.view.View.VISIBLE);
            aiResponseText.setText(interpretation);
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        startBackgroundThread();
        if (cameraPreview.isAvailable()) {
            openCamera();
        } else {
            cameraPreview.setSurfaceTextureListener(surfaceTextureListener);
        }
    }

    @Override
    protected void onPause() {
        closeCamera();
        stopBackgroundThread();
        super.onPause();
    }

    private void closeCamera() {
        if (cameraCaptureSession != null) {
            cameraCaptureSession.close();
            cameraCaptureSession = null;
        }
        if (cameraDevice != null) {
            cameraDevice.close();
            cameraDevice = null;
        }
    }

    private void startBackgroundThread() {
        backgroundThread = new HandlerThread("Camera Background");
        backgroundThread.start();
        backgroundHandler = new Handler(backgroundThread.getLooper());
    }

    private void stopBackgroundThread() {
        if (backgroundThread != null) {
            backgroundThread.quitSafely();
            try {
                backgroundThread.join();
                backgroundThread = null;
                backgroundHandler = null;
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
