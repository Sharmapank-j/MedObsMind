# Google OAuth Authentication & Unique User ID System

## Overview

Complete Google OAuth 2.0 authentication system with automatic unique user ID generation for seamless onboarding in MedObsMind.

## Table of Contents

1. [Authentication Architecture](#authentication-architecture)
2. [User Data Model](#user-data-model)
3. [Unique User ID Generation](#unique-user-id-generation)
4. [API Endpoints](#api-endpoints)
5. [Security Implementation](#security-implementation)
6. [Frontend Integration](#frontend-integration)
7. [Database Schema](#database-schema)
8. [Onboarding Flow](#onboarding-flow)

---

## Authentication Architecture

### OAuth 2.0 Flow (Google)

Complete user authentication journey:

```
1. User clicks "Sign in with Google" button
2. Redirect to Google OAuth consent screen
3. User authorizes MedObsMind access
4. Google redirects back with authorization code
5. Backend exchanges code for access token
6. Backend verifies token with Google API
7. Extract user profile (email, name, picture)
8. Check if user exists (by google_id or email)
9. Generate unique user ID (if new user)
10. Create/update user record in database
11. Generate JWT session token
12. Return user profile + JWT to frontend
13. Frontend stores JWT in secure storage
14. Subsequent requests include JWT in header
```

### System Architecture

```
┌─────────────┐
│   User      │
│  (Browser/  │
│   Mobile)   │
└──────┬──────┘
       │ 1. Click "Sign in with Google"
       ▼
┌─────────────────────────────────────┐
│   MedObsMind Frontend              │
│   (Web/Android/iOS)                │
└──────┬──────────────────────────────┘
       │ 2. Redirect to Google OAuth
       ▼
┌─────────────────────────────────────┐
│   Google OAuth Server               │
│   accounts.google.com               │
└──────┬──────────────────────────────┘
       │ 3. User authorizes + return code
       ▼
┌─────────────────────────────────────┐
│   MedObsMind Backend               │
│   - Verify token                    │
│   - Generate unique user ID         │
│   - Create/update user              │
│   - Issue JWT token                 │
└──────┬──────────────────────────────┘
       │ 4. Return user + JWT
       ▼
┌─────────────────────────────────────┐
│   User Dashboard                    │
│   (Authenticated session)           │
└─────────────────────────────────────┘
```

---

## User Data Model

Complete user schema with Google integration:

```python
class User:
    # Primary identifiers
    id: int  # Auto-increment, internal only
    unique_user_id: str  # MOM-UUID4, public-facing
    email: str  # Unique, from Google
    
    # OAuth data
    google_id: str  # Unique, sub from Google JWT
    google_email_verified: bool
    
    # Profile data (from Google)
    name: str
    given_name: str
    family_name: str
    picture_url: str
    locale: str  # e.g., "en", "hi"
    
    # Additional profile (user-provided)
    status: enum  # public, professional
    role: enum  # doctor, student, nurse, patient
    phone: str  # Optional
    date_of_birth: date
    age: int
    gender: enum
    
    # Professional data
    qualification: str
    institution: str
    license_number: str  # For professionals
    specialization: str
    experience_years: int
    
    # Location
    country: str
    state: str
    city: str
    
    # Preferences
    preferred_language: str  # Default from Google locale
    hobbies: JSON
    interests: JSON
    
    # System fields
    is_active: bool  # Default True
    is_email_verified: bool  # From Google
    created_at: timestamp
    updated_at: timestamp
    last_login_at: timestamp
    
    # Metadata
    onboarding_completed: bool
    terms_accepted: bool
    terms_accepted_at: timestamp
```

---

## Unique User ID Generation

### Format

**Pattern:** `MOM-{UUID4}`

**Example:** `MOM-550e8400-e29b-41d4-a716-446655440000`

### Characteristics

- ✅ **Globally unique** - UUID4 = 128-bit random
- ✅ **Human-readable prefix** - MOM = MedObsMind
- ✅ **Immutable** - Never changes after creation
- ✅ **Public-safe** - Used in all public-facing APIs
- ✅ **Database indexed** - Fast lookup
- ✅ **Collision-resistant** - ~1 in 2^122 probability

### Generation Algorithm

```python
import uuid

def generate_unique_user_id() -> str:
    """
    Generate unique user ID in format MOM-{UUID4}
    
    Returns:
        str: Unique user ID (e.g., MOM-550e8400-e29b-41d4-a716-446655440000)
    """
    return f"MOM-{uuid.uuid4()}"

# Usage in user creation
user_id = generate_unique_user_id()
# Result: MOM-550e8400-e29b-41d4-a716-446655440000
```

### Why UUID4?

1. **No coordination needed** - Generate anywhere, anytime
2. **Offline generation** - Works without network
3. **Cryptographically secure** - Uses OS random source
4. **Standard format** - RFC 4122 compliant
5. **Database support** - Native UUID type in PostgreSQL
6. **Zero collision risk** - 2^122 possible values

---

## API Endpoints

### 1. Initiate Google OAuth

```http
GET /api/v1/auth/google/login

Response: Redirect to Google OAuth
Location: https://accounts.google.com/o/oauth2/v2/auth?
  client_id=YOUR_CLIENT_ID&
  redirect_uri=https://app.medobsmind.ai/auth/google/callback&
  response_type=code&
  scope=openid email profile&
  access_type=offline
```

### 2. OAuth Callback

```http
GET /api/v1/auth/google/callback?code=AUTHORIZATION_CODE

Backend Process:
1. Exchange code for access token
2. Verify token with Google
3. Extract user profile
4. Create/update user
5. Generate JWT
6. Redirect to app with token

Response: Redirect to frontend
Location: https://app.medobsmind.ai/dashboard?token=JWT_TOKEN
```

### 3. Verify Google Token

```http
POST /api/v1/auth/google/verify
Content-Type: application/json

Request Body:
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
}

Response (200 OK):
{
  "success": true,
  "user": {
    "unique_user_id": "MOM-550e8400-e29b-41d4-a716-446655440000",
    "email": "doctor@example.com",
    "name": "Dr. Rajesh Kumar",
    "picture": "https://lh3.googleusercontent.com/...",
    "status": "professional",
    "role": "doctor",
    "onboarding_completed": false
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "refresh_token": "def50200abcd...",
  "token_type": "Bearer",
  "expires_in": 86400
}

Error Response (401 Unauthorized):
{
  "success": false,
  "error": "invalid_token",
  "message": "Google token verification failed"
}
```

### 4. Get Current User Profile

```http
GET /api/v1/auth/me
Authorization: Bearer {JWT_TOKEN}

Response (200 OK):
{
  "unique_user_id": "MOM-550e8400-e29b-41d4-a716-446655440000",
  "email": "doctor@example.com",
  "name": "Dr. Rajesh Kumar",
  "picture": "https://lh3.googleusercontent.com/...",
  "status": "professional",
  "role": "doctor",
  "qualification": "MBBS, MD",
  "specialization": "Cardiology",
  "experience_years": 10,
  "preferred_language": "en",
  "onboarding_completed": true,
  "created_at": "2024-01-15T10:30:00Z",
  "last_login_at": "2024-02-06T09:15:00Z"
}

Error Response (401 Unauthorized):
{
  "error": "unauthorized",
  "message": "Invalid or expired token"
}
```

### 5. Complete Onboarding

```http
POST /api/v1/auth/onboarding/complete
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

Request Body:
{
  "status": "professional",
  "role": "doctor",
  "qualification": "MBBS, MD",
  "institution": "AIIMS Delhi",
  "license_number": "MCI-12345",
  "specialization": "Cardiology",
  "experience_years": 10,
  "phone": "+91-9876543210",
  "date_of_birth": "1985-05-15",
  "gender": "male",
  "city": "Delhi",
  "state": "Delhi",
  "country": "India",
  "preferred_language": "en",
  "terms_accepted": true
}

Response (200 OK):
{
  "success": true,
  "user": {
    "unique_user_id": "MOM-550e8400-e29b-41d4-a716-446655440000",
    "onboarding_completed": true,
    "profile_complete": true
  }
}
```

### 6. Update Profile

```http
PUT /api/v1/auth/profile
Authorization: Bearer {JWT_TOKEN}
Content-Type: application/json

Request Body:
{
  "phone": "+91-9876543210",
  "hobbies": ["Reading", "Yoga"],
  "professional_interests": ["Cardiology", "AI in Medicine"],
  "preferred_language": "hi"
}

Response (200 OK):
{
  "success": true,
  "user": {
    "unique_user_id": "MOM-550e8400-e29b-41d4-a716-446655440000",
    "phone": "+91-9876543210",
    "preferred_language": "hi",
    "updated_at": "2024-02-06T10:30:00Z"
  }
}
```

### 7. Logout

```http
POST /api/v1/auth/logout
Authorization: Bearer {JWT_TOKEN}

Response (200 OK):
{
  "success": true,
  "message": "Logged out successfully"
}
```

### 8. Refresh Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

Request Body:
{
  "refresh_token": "def50200abcd..."
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
  "refresh_token": "def50200xyz...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

---

## Security Implementation

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "MOM-550e8400-e29b-41d4-a716-446655440000",
    "email": "doctor@example.com",
    "role": "doctor",
    "status": "professional",
    "iat": 1707209400,
    "exp": 1707295800
  },
  "signature": "..."
}
```

### Security Features

- ✅ **HTTPS only** - TLS 1.3 encryption
- ✅ **JWT expiration** - 24 hours for access token
- ✅ **Refresh tokens** - 7-day expiration
- ✅ **Secure cookies** - httpOnly, SameSite=Strict (web)
- ✅ **Encrypted storage** - Keychain (iOS), Keystore (Android)
- ✅ **Rate limiting** - 5 requests/minute per IP
- ✅ **IP monitoring** - Suspicious activity detection
- ✅ **CSRF protection** - Tokens for state mutation
- ✅ **XSS protection** - Security headers
- ✅ **Audit logging** - All auth events logged

### Google OAuth Token Verification

```python
from google.oauth2 import id_token
from google.auth.transport import requests

def verify_google_token(token: str) -> dict:
    """
    Verify Google ID token and extract user information
    
    Args:
        token: Google ID token from client
        
    Returns:
        dict: User information from Google
        
    Raises:
        ValueError: If token is invalid
    """
    try:
        # Verify token with Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Verify issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer')
        
        # Extract and return user info
        return {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'email_verified': idinfo.get('email_verified', False),
            'name': idinfo.get('name'),
            'given_name': idinfo.get('given_name'),
            'family_name': idinfo.get('family_name'),
            'picture': idinfo.get('picture'),
            'locale': idinfo.get('locale', 'en')
        }
    except ValueError as e:
        # Token verification failed
        return None
```

---

## Frontend Integration

### Web (React)

**Installation:**
```bash
npm install @react-oauth/google
```

**Implementation:**
```javascript
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';

function LoginPage() {
  const navigate = useNavigate();

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      // Send ID token to backend
      const response = await fetch('/api/v1/auth/google/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_token: credentialResponse.credential
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Store JWT token securely
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        
        // Store user info
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Check if onboarding needed
        if (!data.user.onboarding_completed) {
          navigate('/onboarding');
        } else {
          navigate('/dashboard');
        }
      } else {
        alert('Login failed: ' + data.message);
      }
    } catch (error) {
      console.error('Login failed:', error);
      alert('An error occurred during login');
    }
  };

  const handleGoogleError = () => {
    console.log('Login Failed');
    alert('Google login failed. Please try again.');
  };

  return (
    <div className="login-page">
      <h1>Welcome to MedObsMind</h1>
      <p>Sign in to continue</p>
      
      <GoogleOAuthProvider clientId="YOUR_GOOGLE_CLIENT_ID">
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          useOneTap
          theme="filled_blue"
          size="large"
          text="signin_with"
          shape="rectangular"
        />
      </GoogleOAuthProvider>
    </div>
  );
}

export default LoginPage;
```

### Android (Kotlin)

**Gradle dependencies:**
```kotlin
// build.gradle (app level)
dependencies {
    implementation 'com.google.android.gms:play-services-auth:20.7.0'
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
}
```

**Implementation:**
```kotlin
import com.google.android.gms.auth.api.signin.*
import com.google.android.gms.common.api.ApiException
import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log

class MainActivity : AppCompatActivity() {
    private lateinit var googleSignInClient: GoogleSignInClient
    private val RC_SIGN_IN = 9001
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Configure Google Sign-In
        val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestIdToken(getString(R.string.google_client_id))
            .requestEmail()
            .requestProfile()
            .build()
        
        googleSignInClient = GoogleSignIn.getClient(this, gso)
        
        // Sign-in button click
        findViewById<SignInButton>(R.id.sign_in_button).setOnClickListener {
            signIn()
        }
        
        // Check if already signed in
        checkExistingSignIn()
    }
    
    private fun checkExistingSignIn() {
        val account = GoogleSignIn.getLastSignedInAccount(this)
        if (account != null) {
            // User already signed in
            updateUI(account)
        }
    }
    
    private fun signIn() {
        val signInIntent = googleSignInClient.signInIntent
        startActivityForResult(signInIntent, RC_SIGN_IN)
    }
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        
        if (requestCode == RC_SIGN_IN) {
            val task = GoogleSignIn.getSignedInAccountFromIntent(data)
            handleSignInResult(task)
        }
    }
    
    private fun handleSignInResult(completedTask: Task<GoogleSignInAccount>) {
        try {
            val account = completedTask.getResult(ApiException::class.java)
            val idToken = account?.idToken
            
            if (idToken != null) {
                // Send to backend for verification
                verifyTokenWithBackend(idToken)
            } else {
                Log.w(TAG, "ID Token is null")
            }
        } catch (e: ApiException) {
            Log.w(TAG, "signInResult:failed code=" + e.statusCode)
            updateUI(null)
        }
    }
    
    private fun verifyTokenWithBackend(idToken: String) {
        lifecycleScope.launch {
            try {
                val request = VerifyTokenRequest(idToken)
                val response = apiService.verifyGoogleToken(request)
                
                if (response.success) {
                    // Store tokens securely
                    securePreferences.saveAccessToken(response.access_token)
                    securePreferences.saveRefreshToken(response.refresh_token)
                    
                    // Store user data
                    securePreferences.saveUser(response.user)
                    
                    // Navigate based on onboarding status
                    if (!response.user.onboarding_completed) {
                        startActivity(Intent(this@MainActivity, OnboardingActivity::class.java))
                    } else {
                        startActivity(Intent(this@MainActivity, DashboardActivity::class.java))
                    }
                    finish()
                } else {
                    Log.e(TAG, "Backend verification failed: ${response.message}")
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error verifying token", e)
            }
        }
    }
    
    private fun updateUI(account: GoogleSignInAccount?) {
        if (account != null) {
            // User signed in
            findViewById<TextView>(R.id.status).text = 
                "Signed in as: ${account.displayName}"
        } else {
            // User signed out
            findViewById<TextView>(R.id.status).text = "Signed out"
        }
    }
    
    companion object {
        private const val TAG = "MainActivity"
    }
}
```

### iOS (Swift)

**Installation (CocoaPods):**
```ruby
pod 'GoogleSignIn'
```

**Implementation:**
```swift
import UIKit
import GoogleSignIn

class LoginViewController: UIViewController {
    
    @IBOutlet weak var signInButton: GIDSignInButton!
    @IBOutlet weak var statusLabel: UILabel!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Configure Google Sign-In
        guard let clientID = Bundle.main.object(forInfoDictionaryKey: "GIDClientID") as? String else {
            return
        }
        
        let config = GIDConfiguration(clientID: clientID)
        GIDSignIn.sharedInstance.configuration = config
        
        // Check if already signed in
        GIDSignIn.sharedInstance.restorePreviousSignIn { user, error in
            if error != nil || user == nil {
                // Show sign-in
                self.statusLabel.text = "Not signed in"
            } else {
                // User already signed in
                self.handleSignedInUser(user: user)
            }
        }
        
        // Setup sign-in button
        signInButton.style = .wide
    }
    
    @IBAction func signInTapped(_ sender: UIButton) {
        GIDSignIn.sharedInstance.signIn(withPresenting: self) { result, error in
            guard error == nil else {
                print("Error signing in: \(error!.localizedDescription)")
                return
            }
            
            guard let user = result?.user,
                  let idToken = user.idToken?.tokenString else {
                return
            }
            
            // Send to backend for verification
            self.verifyTokenWithBackend(idToken: idToken)
        }
    }
    
    func verifyTokenWithBackend(idToken: String) {
        guard let url = URL(string: "https://api.medobsmind.ai/api/v1/auth/google/verify") else {
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: String] = ["id_token": idToken]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            guard let data = data,
                  error == nil,
                  let authResponse = try? JSONDecoder().decode(AuthResponse.self, from: data) else {
                print("Error verifying token")
                return
            }
            
            if authResponse.success {
                // Store tokens in Keychain
                KeychainHelper.save(token: authResponse.access_token, for: "access_token")
                KeychainHelper.save(token: authResponse.refresh_token, for: "refresh_token")
                
                // Store user data
                UserDefaults.standard.set(try? JSONEncoder().encode(authResponse.user), forKey: "user")
                
                DispatchQueue.main.async {
                    if !authResponse.user.onboarding_completed {
                        self.navigateToOnboarding()
                    } else {
                        self.navigateToDashboard()
                    }
                }
            }
        }.resume()
    }
    
    func handleSignedInUser(user: GIDGoogleUser?) {
        guard let user = user else { return }
        statusLabel.text = "Signed in as: \(user.profile?.name ?? "Unknown")"
    }
    
    func navigateToOnboarding() {
        let storyboard = UIStoryboard(name: "Main", bundle: nil)
        let vc = storyboard.instantiateViewController(withIdentifier: "OnboardingViewController")
        navigationController?.pushViewController(vc, animated: true)
    }
    
    func navigateToDashboard() {
        let storyboard = UIStoryboard(name: "Main", bundle: nil)
        let vc = storyboard.instantiateViewController(withIdentifier: "DashboardViewController")
        navigationController?.pushViewController(vc, animated: true)
    }
}

// Auth response model
struct AuthResponse: Codable {
    let success: Bool
    let user: User
    let access_token: String
    let refresh_token: String
    let token_type: String
    let expires_in: Int
}

struct User: Codable {
    let unique_user_id: String
    let email: String
    let name: String
    let picture: String?
    let status: String?
    let role: String?
    let onboarding_completed: Bool
}
```

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    -- Primary identifiers
    id SERIAL PRIMARY KEY,
    unique_user_id VARCHAR(50) UNIQUE NOT NULL,  -- MOM-UUID format
    google_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    google_email_verified BOOLEAN DEFAULT FALSE,
    
    -- Profile from Google
    name VARCHAR(255),
    given_name VARCHAR(100),
    family_name VARCHAR(100),
    picture_url TEXT,
    locale VARCHAR(10),
    
    -- Additional profile
    status VARCHAR(20),  -- public, professional
    role VARCHAR(50),  -- doctor, student, nurse, patient
    phone VARCHAR(20),
    date_of_birth DATE,
    age INTEGER,
    gender VARCHAR(20),
    
    -- Professional data
    qualification TEXT,
    institution VARCHAR(255),
    license_number VARCHAR(100),
    specialization VARCHAR(100),
    experience_years INTEGER,
    
    -- Location
    country VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(100),
    
    -- Preferences
    preferred_language VARCHAR(10) DEFAULT 'en',
    hobbies JSONB,
    interests JSONB,
    
    -- System fields
    is_active BOOLEAN DEFAULT TRUE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    terms_accepted BOOLEAN DEFAULT FALSE,
    terms_accepted_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_unique_user_id ON users(unique_user_id);
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status_role ON users(status, role);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### OAuth Providers Table

```sql
CREATE TABLE oauth_providers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,  -- google, facebook, apple
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(provider, provider_user_id)
);

CREATE INDEX idx_oauth_user_id ON oauth_providers(user_id);
CREATE INDEX idx_oauth_provider ON oauth_providers(provider, provider_user_id);
```

### User Sessions Table

```sql
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(500) UNIQUE NOT NULL,
    refresh_token VARCHAR(500),
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_type VARCHAR(50),  -- web, android, ios
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_user_active ON user_sessions(user_id, is_active);
CREATE INDEX idx_sessions_expires_at ON user_sessions(expires_at);
```

---

## Onboarding Flow

### Step-by-Step Process

```
┌─────────────────────────────────────────┐
│ Step 1: Google Sign-In                  │
│ - User clicks "Sign in with Google"     │
│ - Redirect to Google OAuth               │
│ - User authorizes                        │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│ Step 2: User Creation                    │
│ - Generate unique ID (MOM-UUID)         │
│ - Extract Google profile                 │
│ - Create user record                     │
│ - Generate JWT token                     │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│ Step 3: Status Selection                 │
│ - Public or Professional?                │
│ - Show appropriate form                  │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│ Step 4: Role Selection                   │
│ - Doctor, Student, Nurse, Patient, etc. │
│ - Role-specific fields appear            │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│ Step 5: Professional Details (if pro)    │
│ - Qualification, Institution             │
│ - License number                         │
│ - Specialization                         │
│ - Experience                             │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│ Step 6: Additional Details               │
│ - Phone, Date of birth                   │
│ - Location                               │
│ - Language preference                    │
│ - Hobbies/Interests                      │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│ Step 7: Terms & Conditions               │
│ - Privacy policy                         │
│ - Terms of service                       │
│ - Data usage consent                     │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│ Step 8: Complete                         │
│ - Mark onboarding_completed = true       │
│ - Redirect to dashboard                  │
└─────────────────────────────────────────┘
```

### Onboarding Screen Examples

#### Screen 1: Welcome

```
╔═══════════════════════════════════════╗
║                                       ║
║        Welcome to MedObsMind!         ║
║                                       ║
║   Let's set up your account           ║
║                                       ║
║   ┌───────────────────────────────┐  ║
║   │  [G] Continue with Google     │  ║
║   └───────────────────────────────┘  ║
║                                       ║
║   Secure • Fast • Professional        ║
║                                       ║
╚═══════════════════════════════════════╝
```

#### Screen 2: Status Selection

```
╔═══════════════════════════════════════╗
║   I am a...                           ║
║                                       ║
║   ┌─────────────────────────────┐    ║
║   │  👤 Public User             │    ║
║   │  Health-conscious individual│    ║
║   └─────────────────────────────┘    ║
║                                       ║
║   ┌─────────────────────────────┐    ║
║   │  👨‍⚕️ Healthcare Professional  │    ║
║   │  Doctor, Student, Nurse, etc│    ║
║   └─────────────────────────────┘    ║
║                                       ║
║                    [Next] ──────────▶ ║
╚═══════════════════════════════════════╝
```

#### Screen 3: Professional Role

```
╔═══════════════════════════════════════╗
║   Your Role                           ║
║                                       ║
║   ( ) Doctor                          ║
║   (•) Medical Student                 ║
║   ( ) Resident/Intern                 ║
║   ( ) Nurse                           ║
║   ( ) Researcher                      ║
║                                       ║
║   ◀──────── [Back]    [Next] ───────▶ ║
╚═══════════════════════════════════════╝
```

---

## Configuration

### Environment Variables

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://api.medobsmind.ai/api/v1/auth/google/callback

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/medobsmind

# Frontend URLs (for CORS)
FRONTEND_URL=https://app.medobsmind.ai
CORS_ORIGINS=https://app.medobsmind.ai,https://medobsmind.ai

# Session
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Strict
```

### Google Cloud Console Setup

1. **Create OAuth 2.0 Client**
   - Go to Google Cloud Console
   - Enable Google+ API
   - Create OAuth 2.0 Client ID
   - Type: Web application
   - Authorized JavaScript origins: https://app.medobsmind.ai
   - Authorized redirect URIs: https://api.medobsmind.ai/api/v1/auth/google/callback

2. **Configure Consent Screen**
   - App name: MedObsMind
   - Support email
   - App logo
   - Scopes: openid, email, profile

3. **Get Credentials**
   - Download client ID and secret
   - Add to environment variables

---

## Best Practices

### Security

1. **Never log sensitive data** - Don't log tokens or passwords
2. **Validate all inputs** - Sanitize user-provided data
3. **Use HTTPS everywhere** - No HTTP in production
4. **Rotate secrets regularly** - JWT secret, Google client secret
5. **Implement rate limiting** - Prevent brute force
6. **Monitor suspicious activity** - Failed login attempts, unusual locations
7. **Use secure session storage** - httpOnly cookies, encrypted mobile storage

### User Experience

1. **One-click sign-in** - Google button on landing page
2. **Clear error messages** - "Login failed" → "Google sign-in was cancelled"
3. **Loading states** - Show spinner during OAuth flow
4. **Remember user** - Use refresh tokens for seamless experience
5. **Graceful degradation** - Handle network errors
6. **Mobile-friendly** - Large touch targets, native OAuth flows

### Performance

1. **Cache user profiles** - Reduce database queries
2. **Index frequently queried fields** - unique_user_id, email
3. **Use connection pooling** - PostgreSQL connections
4. **Implement CDN** - Profile pictures from Google
5. **Lazy load** - Only fetch data when needed

---

## Testing

### Unit Tests

```python
import pytest
from app.services.auth_service import generate_unique_user_id, verify_google_token

def test_generate_unique_user_id():
    """Test unique user ID generation"""
    user_id = generate_unique_user_id()
    assert user_id.startswith("MOM-")
    assert len(user_id) == 40  # MOM- (4) + UUID4 (36)
    
    # Test uniqueness
    user_ids = set()
    for _ in range(1000):
        user_ids.add(generate_unique_user_id())
    assert len(user_ids) == 1000  # All unique

def test_verify_google_token_valid():
    """Test Google token verification with valid token"""
    # Mock Google API response
    with mock.patch('google.oauth2.id_token.verify_oauth2_token') as mock_verify:
        mock_verify.return_value = {
            'iss': 'accounts.google.com',
            'sub': '1234567890',
            'email': 'test@example.com',
            'email_verified': True,
            'name': 'Test User'
        }
        
        result = verify_google_token('valid_token')
        assert result is not None
        assert result['google_id'] == '1234567890'
        assert result['email'] == 'test@example.com'

def test_verify_google_token_invalid():
    """Test Google token verification with invalid token"""
    result = verify_google_token('invalid_token')
    assert result is None
```

### Integration Tests

```python
def test_google_auth_flow(client):
    """Test complete Google OAuth flow"""
    # Step 1: Verify token
    response = client.post('/api/v1/auth/google/verify', json={
        'id_token': 'mock_google_token'
    })
    assert response.status_code == 200
    data = response.json()
    assert 'access_token' in data
    assert 'user' in data
    assert data['user']['unique_user_id'].startswith('MOM-')
    
    # Step 2: Access protected endpoint
    token = data['access_token']
    response = client.get('/api/v1/auth/me', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert response.json()['email'] == 'test@example.com'
    
    # Step 3: Complete onboarding
    response = client.post('/api/v1/auth/onboarding/complete', 
        headers={'Authorization': f'Bearer {token}'},
        json={
            'status': 'professional',
            'role': 'doctor',
            'terms_accepted': True
        }
    )
    assert response.status_code == 200
    assert response.json()['user']['onboarding_completed'] == True
```

---

## Troubleshooting

### Common Issues

**1. "Invalid token" error**
- Check Google Client ID matches
- Verify token hasn't expired
- Ensure HTTPS is used

**2. "User not found"**
- Check if user was created in database
- Verify unique_user_id generation
- Check database connection

**3. OAuth redirect fails**
- Verify redirect URI in Google Console
- Check CORS configuration
- Ensure HTTPS on production

**4. Session expires too quickly**
- Check JWT_ACCESS_TOKEN_EXPIRE_MINUTES
- Implement refresh token logic
- Use "Remember me" option

**5. Onboarding doesn't save**
- Check database constraints
- Verify all required fields
- Check API validation

---

## Conclusion

This comprehensive Google OAuth integration provides:

- ✅ Secure authentication with Google
- ✅ Automatic unique user ID generation (MOM-UUID)
- ✅ Complete onboarding flow
- ✅ Profile management
- ✅ Session handling (JWT + refresh tokens)
- ✅ Multi-platform support (Web, Android, iOS)
- ✅ GDPR/DPDP compliant
- ✅ Scalable architecture

**Implementation time:** 2-3 days for backend + frontend
**Maintenance:** Minimal (Google handles most security)
**User experience:** Seamless one-click sign-in

**Next steps:**
1. Set up Google Cloud Console
2. Implement backend endpoints
3. Create frontend components
4. Test OAuth flow end-to-end
5. Deploy and monitor

---

**Documentation Version:** 1.0  
**Last Updated:** February 6, 2026  
**Author:** MedObsMind Development Team
