# MedObsMind - User & Admin Interface Specifications

## 🎯 Dual Interface Architecture

MedObsMind provides **two distinct interfaces** for different user types:

1. **User Interface** - For doctors, students, patients, hospital staff
2. **Admin Interface** - For developers, administrators, system managers

---

## 👥 User Interface (UI)

### Purpose
Primary interface for healthcare professionals and students to:
- Monitor patients
- View vitals and alerts
- Get AI recommendations
- Access educational content
- Clinical decision support

### Target Users
- 👨‍⚕️ **Doctors** - Clinical decision support, patient monitoring
- 👨‍🎓 **Medical Students** - Education mode, case studies
- 👩‍⚕️ **Nurses** - Vitals entry, patient care
- 🏥 **Hospital Staff** - Limited access to patient data
- 🧑‍💼 **Patients** - View own health records (future)

### Access Control
- **Authentication:** Email/phone + password
- **Role-based access:** Doctor, Resident, Student, Nurse, Patient
- **Permissions:** Based on role and department
- **No admin functions visible**

---

## 🔧 Admin Interface (AI)

### Purpose
Management and monitoring interface for:
- System configuration
- User management
- Performance monitoring
- Data analytics
- Model training management
- Device configuration
- Security and compliance

### Target Users
- 👨‍💻 **Developer** - You (primary admin)
- 🛠️ **System Administrators** - Hospital IT staff
- 📊 **Data Scientists** - Model performance analysis
- 🔒 **Security Auditors** - Compliance monitoring

### Access Control
- **Authentication:** Multi-factor authentication (MFA)
- **Role-based access:** Super Admin, Admin, Developer, Auditor
- **IP whitelist:** Restrict to specific IPs
- **Audit logging:** All admin actions logged
- **Session timeout:** Shorter timeout (15 minutes)

---

## 📱 Interface Comparison

| Feature | User Interface | Admin Interface |
|---------|---------------|-----------------|
| **Access URL** | `app.medobsmind.ai` | `admin.medobsmind.ai` |
| **Authentication** | Email + Password | Email + Password + MFA |
| **Patient Data** | Clinical view | Full database access |
| **Analytics** | Basic (own patients) | Complete system analytics |
| **Configuration** | ❌ No access | ✅ Full control |
| **User Management** | ❌ No access | ✅ Create/edit/delete users |
| **Model Training** | ❌ No access | ✅ Trigger training, view metrics |
| **Logs** | ❌ No access | ✅ Full system logs |
| **API Keys** | ❌ No access | ✅ Generate/revoke keys |
| **Billing** | ❌ No access | ✅ Usage and billing |
| **Updates** | ❌ No access | ✅ Deploy updates |

---

## 🌐 Website Implementation

### User Website (Landing Page) ✅
**URL:** `https://medobsmind.ai`
**Current Status:** Complete (`index.html`)

**Features:**
- Marketing content
- Product information
- Features showcase
- Pricing
- Contact form
- Login button → redirects to web app

**No admin functions**

### Admin Portal Website (New)
**URL:** `https://admin.medobsmind.ai`
**Current Status:** ❌ Need to create

**Features:**
```html
admin-portal/
├── index.html          # Admin login
├── dashboard.html      # System overview
├── users.html          # User management
├── analytics.html      # System analytics
├── models.html         # AI model management
├── devices.html        # IoT device management
├── logs.html           # System logs
├── settings.html       # Configuration
└── assets/
    ├── admin.css       # Admin-specific styling
    └── admin.js        # Admin functionality
```

---

## 💻 Web App Implementation

### User Web App (React Dashboard)
**URL:** `https://app.medobsmind.ai`
**Current Status:** ❌ Need to create

**Structure:**
```javascript
web-app/
├── src/
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx       # Patient overview
│   │   ├── PatientList.jsx     # All patients
│   │   ├── PatientDetail.jsx   # Single patient
│   │   ├── VitalsMonitor.jsx   # Real-time vitals
│   │   ├── Alerts.jsx          # Alert management
│   │   ├── Education.jsx       # Student mode
│   │   └── Profile.jsx         # User profile
│   ├── components/
│   │   ├── VitalsChart.jsx
│   │   ├── AlertCard.jsx
│   │   ├── PatientCard.jsx
│   │   └── Navigation.jsx
│   └── services/
│       └── api.js              # Backend API calls
```

**Key Features:**
- Real-time patient monitoring
- Vitals charts and trends
- Alert notifications
- AI recommendations
- Education mode for students
- Multi-language support

**Access Control:**
```javascript
// Role-based component rendering
const Dashboard = () => {
  const { user } = useAuth();
  
  return (
    <>
      {user.role === 'doctor' && <DoctorDashboard />}
      {user.role === 'student' && <StudentDashboard />}
      {user.role === 'nurse' && <NurseDashboard />}
    </>
  );
};
```

### Admin Web App (React Dashboard)
**URL:** `https://admin.medobsmind.ai`
**Current Status:** ❌ Need to create

**Structure:**
```javascript
admin-web-app/
├── src/
│   ├── pages/
│   │   ├── AdminLogin.jsx      # MFA login
│   │   ├── SystemDashboard.jsx # System metrics
│   │   ├── UserManagement.jsx  # CRUD users
│   │   ├── HospitalManagement.jsx
│   │   ├── ModelManagement.jsx # AI models
│   │   ├── DeviceManagement.jsx # IoT devices
│   │   ├── Analytics.jsx       # Usage analytics
│   │   ├── Logs.jsx            # System logs
│   │   ├── Security.jsx        # Security settings
│   │   ├── Billing.jsx         # Usage & billing
│   │   └── Settings.jsx        # System config
│   ├── components/
│   │   ├── MetricsCard.jsx
│   │   ├── UserTable.jsx
│   │   ├── LogViewer.jsx
│   │   └── AdminNav.jsx
│   └── services/
│       └── adminApi.js         # Admin API calls
```

**Key Features:**
- System performance metrics
- User and hospital management
- AI model training dashboard
- Device configuration
- Real-time system logs
- Security monitoring
- Usage analytics
- Billing and subscriptions

**Access Control:**
```javascript
// Admin-only routes with MFA
const AdminRoute = ({ children }) => {
  const { user, mfaVerified } = useAuth();
  
  if (!user || user.role !== 'admin' || !mfaVerified) {
    return <Navigate to="/admin/login" />;
  }
  
  return children;
};
```

---

## 📱 Android App Implementation

### User Android App
**Package:** `com.medobsmind.app`
**Current Status:** ⚠️ Structure complete, UI 40%

**Activities/Screens:**
```kotlin
app/src/main/java/com/medobsmind/app/
├── ui/
│   ├── user/
│   │   ├── LoginActivity.kt
│   │   ├── DashboardActivity.kt
│   │   ├── PatientListActivity.kt
│   │   ├── PatientDetailActivity.kt
│   │   ├── VitalsMonitorActivity.kt
│   │   ├── AlertsActivity.kt
│   │   ├── EducationActivity.kt      # Student mode
│   │   └── ProfileActivity.kt
│   ├── viewmodel/
│   │   ├── DashboardViewModel.kt
│   │   ├── PatientViewModel.kt
│   │   └── VitalsViewModel.kt
│   └── fragments/
│       ├── VitalsChartFragment.kt
│       └── AlertListFragment.kt
```

**User Features:**
- Patient monitoring on mobile
- Quick vitals entry
- Real-time alerts
- Offline support
- Voice commands (smart glasses)
- Student education mode

### Admin Android App (Separate)
**Package:** `com.medobsmind.admin`
**Current Status:** ❌ Need to create

**Activities/Screens:**
```kotlin
admin-app/src/main/java/com/medobsmind/admin/
├── ui/
│   ├── AdminLoginActivity.kt      # MFA login
│   ├── SystemDashboardActivity.kt
│   ├── UserManagementActivity.kt
│   ├── HospitalManagementActivity.kt
│   ├── ModelManagementActivity.kt
│   ├── DeviceManagementActivity.kt
│   ├── AnalyticsActivity.kt
│   ├── LogsActivity.kt
│   └── SettingsActivity.kt
├── viewmodel/
│   ├── AdminDashboardViewModel.kt
│   ├── UserManagementViewModel.kt
│   └── SystemMetricsViewModel.kt
└── service/
    └── AdminApiService.kt
```

**Admin Features:**
- System monitoring on-the-go
- Quick user management
- Device status checks
- Alert about system issues
- Emergency configuration changes

---

## 🍎 iOS App Implementation

### User iOS App
**Bundle ID:** `ai.medobsmind.app`
**Current Status:** ❌ Need to create

**Structure:**
```swift
ios/MedObsMind/
├── Views/
│   ├── Auth/
│   │   └── LoginView.swift
│   ├── Dashboard/
│   │   └── DashboardView.swift
│   ├── Patients/
│   │   ├── PatientListView.swift
│   │   └── PatientDetailView.swift
│   ├── Vitals/
│   │   └── VitalsMonitorView.swift
│   ├── Alerts/
│   │   └── AlertsView.swift
│   └── Education/
│       └── EducationView.swift
├── ViewModels/
│   ├── DashboardViewModel.swift
│   └── PatientViewModel.swift
└── Services/
    └── APIService.swift
```

### Admin iOS App (Separate)
**Bundle ID:** `ai.medobsmind.admin`
**Current Status:** ❌ Need to create

**Structure:**
```swift
ios/MedObsMindAdmin/
├── Views/
│   ├── AdminLogin/
│   │   └── AdminLoginView.swift
│   ├── SystemDashboard/
│   │   └── SystemDashboardView.swift
│   ├── UserManagement/
│   │   └── UserManagementView.swift
│   ├── Analytics/
│   │   └── AnalyticsView.swift
│   └── Settings/
│       └── SettingsView.swift
├── ViewModels/
│   ├── AdminDashboardViewModel.swift
│   └── SystemMetricsViewModel.swift
└── Services/
    └── AdminAPIService.swift
```

---

## 🔑 Authentication & Authorization

### User Authentication

**Login Flow:**
```
1. User enters credentials (email + password)
2. Backend validates credentials
3. Returns JWT token + user role
4. App stores token securely
5. All API calls include token in header
6. Token expires after 24 hours
```

**API Example:**
```javascript
POST /api/v1/auth/login
{
  "email": "doctor@hospital.com",
  "password": "secure_password"
}

Response:
{
  "access_token": "eyJhbGc...",
  "user": {
    "id": 123,
    "name": "Dr. Sharma",
    "role": "doctor",
    "hospital_id": 45,
    "permissions": ["view_patients", "edit_vitals", "view_alerts"]
  }
}
```

### Admin Authentication

**Login Flow:**
```
1. Admin enters credentials
2. Backend sends MFA code (SMS/Email/Authenticator)
3. Admin enters MFA code
4. Backend validates both credentials + MFA
5. Returns JWT token with admin role
6. Token expires after 15 minutes (shorter)
7. Logs all admin actions
```

**API Example:**
```javascript
POST /api/v1/admin/auth/login
{
  "email": "admin@medobsmind.ai",
  "password": "secure_admin_password"
}

Response:
{
  "mfa_required": true,
  "mfa_session_id": "temp_session_123"
}

POST /api/v1/admin/auth/verify-mfa
{
  "mfa_session_id": "temp_session_123",
  "mfa_code": "123456"
}

Response:
{
  "access_token": "eyJhbGc...",
  "user": {
    "id": 1,
    "name": "Sharmapank J",
    "role": "super_admin",
    "permissions": ["*"]  // All permissions
  }
}
```

---

## 🎨 UI/UX Differences

### User Interface Design

**Theme:**
- Clean, clinical design
- Calming colors (blues, greens)
- High contrast for readability
- Large touch targets for quick access
- Focus on patient data visualization

**Layout:**
- Simple navigation (bottom tabs on mobile)
- Dashboard-first (most used screen)
- Quick access to critical features
- Minimal distractions

**Example Screens:**

**Doctor Dashboard:**
```
┌─────────────────────────────┐
│ MedObsMind      [Alerts: 3] │
├─────────────────────────────┤
│ 🏥 ICU - Ward 3A            │
│                              │
│ ⚠️ HIGH PRIORITY ALERTS      │
│ • Patient 101 - NEWS2: 8    │
│ • Patient 205 - SpO2 < 90%  │
│                              │
│ 📊 MY PATIENTS (12)          │
│ ┌─────────┬─────────────┐   │
│ │ Ram K.  │ NEWS2: 5    │   │
│ │ ICU-101 │ ⚠️ Monitor  │   │
│ └─────────┴─────────────┘   │
│ ┌─────────┬─────────────┐   │
│ │ Priya M.│ NEWS2: 2    │   │
│ │ ICU-102 │ ✅ Stable   │   │
│ └─────────┴─────────────┘   │
│                              │
│ [Patients] [Alerts] [Profile]│
└─────────────────────────────┘
```

### Admin Interface Design

**Theme:**
- Professional, dashboard-heavy
- Darker theme (less eye strain)
- Information-dense
- Multiple panels and widgets
- Focus on metrics and system health

**Layout:**
- Complex navigation (sidebar)
- Multi-panel dashboards
- Advanced filtering and search
- Data tables and charts

**Example Screens:**

**Admin Dashboard:**
```
┌───────────────────────────────────────────┐
│ MedObsMind Admin  [You: Super Admin]     │
├─────────────────────────────────────────────┤
│ ☰ Menu                    🔔 Alerts: 2    │
├────────┬────────────────────────────────────┤
│ 🏠 Home│ SYSTEM STATUS                      │
│ 👥 Users│ ┌──────────┬──────────┬────────┐ │
│ 🏥 Hosps│ │ Uptime   │ CPU      │ Memory │ │
│ 🤖 Models│ 99.9%    │ 45%      │ 62%    │ │
│ 📱 Devices└──────────┴──────────┴────────┘ │
│ 📊 Analytics                               │
│ 📝 Logs  ACTIVE USERS (Real-time)          │
│ ⚙️ Settings┌──────────────────────────┐   │
│ 🔒 Security│ 🟢 543 doctors online    │   │
│            │ 🟢 1,234 students online │   │
│            │ 🟢 89 hospitals active   │   │
│            └──────────────────────────┘   │
│            RECENT ALERTS                   │
│            • Model training completed      │
│            • New user signup: Apollo AIIMS │
│                                            │
└────────────────────────────────────────────┘
```

---

## 🔒 Security Differences

### User Interface Security

**Features:**
- ✅ Standard password requirements (8+ chars)
- ✅ Session timeout after 24 hours
- ✅ Auto-lock after 5 minutes idle
- ✅ Biometric login (fingerprint/face)
- ✅ Single device login (optional)
- ❌ No MFA required (optional for doctors)

**Data Access:**
- Only assigned patients
- Only own department
- Cannot view system logs
- Cannot access admin functions

### Admin Interface Security

**Features:**
- ✅ Strong password requirements (12+ chars, complex)
- ✅ **Mandatory MFA** (SMS, Email, or Authenticator)
- ✅ Session timeout after 15 minutes
- ✅ Auto-lock after 2 minutes idle
- ✅ IP whitelist (restrict to office/VPN)
- ✅ Device fingerprinting
- ✅ All actions logged with timestamp

**Data Access:**
- All patients (read-only for most admins)
- All hospitals and users
- Full system logs
- Configuration access
- Database access (super admin only)

---

## 📊 Feature Access Matrix

| Feature | User (Doctor) | User (Student) | Admin | Super Admin |
|---------|--------------|----------------|-------|-------------|
| **View Patients** | ✅ Own | ❌ Demo only | ✅ All | ✅ All |
| **Edit Vitals** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| **View Alerts** | ✅ Own | ❌ No | ✅ All | ✅ All |
| **AI Explanations** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Education Mode** | ⚠️ Limited | ✅ Full | ✅ Yes | ✅ Yes |
| **User Management** | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Hospital Management** | ❌ No | ❌ No | ⚠️ View only | ✅ Yes |
| **Model Training** | ❌ No | ❌ No | ⚠️ View only | ✅ Yes |
| **System Logs** | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Configuration** | ❌ No | ❌ No | ⚠️ Limited | ✅ Yes |
| **Database Access** | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Deploy Updates** | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Billing** | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **API Keys** | ❌ No | ❌ No | ⚠️ View only | ✅ Yes |

---

## 🛠️ Implementation Checklist

### User Interface

**Website (Landing)** ✅
- [x] Landing page HTML/CSS/JS
- [x] Responsive design
- [x] SEO optimization
- [ ] Login button → redirect to app

**Web App (React)**
- [ ] Initialize React project
- [ ] Create user dashboard
- [ ] Patient list and detail views
- [ ] Vitals monitoring interface
- [ ] Alert management
- [ ] Education mode
- [ ] User profile and settings

**Android App**
- [x] Project structure
- [x] Build configuration
- [ ] Complete UI screens (40% done)
- [ ] Backend integration
- [ ] Offline mode
- [ ] Push notifications

**iOS App**
- [ ] Create Xcode project
- [ ] SwiftUI screens
- [ ] Backend integration
- [ ] HealthKit integration
- [ ] Notifications

### Admin Interface

**Admin Portal (Static)**
- [ ] Create admin login page
- [ ] System dashboard HTML
- [ ] User management interface
- [ ] Analytics and reports
- [ ] Settings and configuration

**Admin Web App (React)**
- [ ] Initialize React project (separate)
- [ ] Admin dashboard with metrics
- [ ] User CRUD interface
- [ ] Hospital management
- [ ] Model management
- [ ] Device management
- [ ] Real-time logs viewer
- [ ] Analytics dashboards
- [ ] Security settings
- [ ] Billing and usage

**Admin Android App**
- [ ] Create separate project
- [ ] MFA login
- [ ] System monitoring
- [ ] Quick actions
- [ ] Emergency alerts

**Admin iOS App**
- [ ] Create Xcode project (separate)
- [ ] SwiftUI admin screens
- [ ] System monitoring
- [ ] Remote management

---

## 🔗 API Endpoints

### User API Endpoints
```
Authentication:
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me

Patients:
GET    /api/v1/patients
GET    /api/v1/patients/:id
POST   /api/v1/patients
PUT    /api/v1/patients/:id

Vitals:
GET    /api/v1/vitals/patient/:id
POST   /api/v1/vitals
GET    /api/v1/vitals/:id/trends

Alerts:
GET    /api/v1/alerts
GET    /api/v1/alerts/active
POST   /api/v1/alerts/:id/acknowledge

DDMA (AI):
POST   /v1/chat/completions
POST   /v1/completions
GET    /v1/models
```

### Admin API Endpoints
```
Admin Authentication:
POST   /api/v1/admin/auth/login
POST   /api/v1/admin/auth/verify-mfa
POST   /api/v1/admin/auth/logout

User Management:
GET    /api/v1/admin/users
POST   /api/v1/admin/users
PUT    /api/v1/admin/users/:id
DELETE /api/v1/admin/users/:id
GET    /api/v1/admin/users/:id/activity

Hospital Management:
GET    /api/v1/admin/hospitals
POST   /api/v1/admin/hospitals
PUT    /api/v1/admin/hospitals/:id
GET    /api/v1/admin/hospitals/:id/usage

System Metrics:
GET    /api/v1/admin/metrics/system
GET    /api/v1/admin/metrics/performance
GET    /api/v1/admin/metrics/usage

Model Management:
GET    /api/v1/admin/models
POST   /api/v1/admin/models/train
GET    /api/v1/admin/models/:id/performance
POST   /api/v1/admin/models/:id/deploy

Device Management:
GET    /api/v1/admin/devices
PUT    /api/v1/admin/devices/:id/config
POST   /api/v1/admin/devices/:id/update

Logs:
GET    /api/v1/admin/logs/system
GET    /api/v1/admin/logs/errors
GET    /api/v1/admin/logs/audit

Configuration:
GET    /api/v1/admin/config
PUT    /api/v1/admin/config

Billing:
GET    /api/v1/admin/billing/usage
GET    /api/v1/admin/billing/invoices
```

---

## 🚀 Deployment Strategy

### User Interfaces
- **Subdomain:** `app.medobsmind.ai`
- **Hosting:** AWS/Azure/GCP (high availability)
- **CDN:** CloudFront/CloudFlare (global)
- **Database:** PostgreSQL (user data)
- **Scale:** 10,000+ concurrent users

### Admin Interfaces
- **Subdomain:** `admin.medobsmind.ai`
- **Hosting:** Separate server (security)
- **VPN:** Required for access (optional)
- **Database:** Same as user (different permissions)
- **Scale:** 10-50 concurrent admins

---

## 📱 App Distribution

### User Apps
- **Android:** Google Play Store (public)
- **iOS:** Apple App Store (public)
- **Web:** Public URL

### Admin Apps
- **Android:** Internal distribution (APK)
- **iOS:** TestFlight (internal)
- **Web:** Password-protected URL

---

## 📊 Summary

| Aspect | User Interface | Admin Interface |
|--------|----------------|-----------------|
| **Purpose** | Clinical use | System management |
| **Users** | 10,000+ | 10-50 |
| **Access** | Public (with login) | Restricted (MFA + IP) |
| **URL** | app.medobsmind.ai | admin.medobsmind.ai |
| **Data** | Own patients only | All system data |
| **Security** | Standard | Enhanced (MFA) |
| **Session** | 24 hours | 15 minutes |
| **Design** | Clean, clinical | Dense, informational |
| **Mobile Apps** | Public stores | Internal only |
| **Priority** | HIGH | MEDIUM |

**Next Steps:**
1. Build user web app (React) - HIGH PRIORITY
2. Complete Android user app UI - HIGH PRIORITY
3. Build admin web app - MEDIUM PRIORITY
4. Create admin mobile apps - LOW PRIORITY

---

**Document Version:** 1.0
**Last Updated:** 2026-02-06
**Owner:** Sharmapank J (Developer/Admin)
