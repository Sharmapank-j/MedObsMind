# MedObsMind - Training Data Location & Management (Admin)

## 🎯 Overview

As the **developer/administrator**, you have full access to:
1. **Training data locations** - Where all training data is stored
2. **Data management tools** - View, organize, and manage training datasets
3. **Training pipeline control** - Trigger training, monitor progress
4. **Data quality monitoring** - Verify data integrity and quality
5. **Feedback data access** - View collected feedback for retraining

---

## 📁 Training Data Locations

### Primary Training Data Repository

```bash
# Main training data directory structure
/data/training/
├── raw/                          # Raw, unprocessed data
│   ├── medical_textbooks/        # Indian medical textbooks (PDF, EPUB)
│   │   ├── harrisons_indian_ed/
│   │   ├── davidsons_indian_ed/
│   │   ├── manipal_manual/
│   │   └── metadata.json
│   ├── guidelines/               # ICMR, AIIMS guidelines
│   │   ├── icmr/
│   │   │   ├── sepsis_2023.pdf
│   │   │   ├── cardiac_care.pdf
│   │   │   └── ...
│   │   ├── aiims/
│   │   │   ├── icu_protocols.pdf
│   │   │   └── ...
│   │   └── metadata.json
│   ├── clinical_cases/           # Real de-identified cases
│   │   ├── icu_cases/
│   │   ├── emergency_cases/
│   │   ├── ward_cases/
│   │   └── metadata.json
│   ├── feedback/                 # User feedback data
│   │   ├── 2024_Q1/
│   │   ├── 2024_Q2/
│   │   ├── 2024_Q3/
│   │   └── metadata.json
│   └── synthetic/                # AI-generated scenarios
│       ├── sepsis_scenarios/
│       ├── cardiac_cases/
│       └── metadata.json
│
├── processed/                    # Cleaned and formatted data
│   ├── instruction_tuning/       # Instruction-input-output format
│   │   ├── train.jsonl          # Training set (90%)
│   │   ├── val.jsonl            # Validation set (10%)
│   │   └── test.jsonl           # Test set (hold-out)
│   ├── rag_knowledge_base/       # For RAG retrieval
│   │   ├── embeddings/
│   │   ├── documents/
│   │   └── index/
│   └── metadata.json
│
├── models/                       # Trained models
│   ├── dsquaremedicalmodel/
│   │   ├── v1.0/
│   │   │   ├── base_model/
│   │   │   ├── lora_adapters/
│   │   │   ├── merged_model/
│   │   │   ├── quantized/
│   │   │   │   ├── q4_k_m.gguf  # 4-bit quantized
│   │   │   │   ├── q8_0.gguf    # 8-bit quantized
│   │   │   │   └── f16.gguf     # Full precision
│   │   │   └── metadata.json
│   │   ├── v1.1/
│   │   └── latest -> v1.1/
│   └── checkpoints/              # Training checkpoints
│       ├── checkpoint-1000/
│       ├── checkpoint-2000/
│       └── best_checkpoint/
│
├── logs/                         # Training logs
│   ├── training_runs/
│   │   ├── 2024-01-15_run1/
│   │   │   ├── tensorboard/
│   │   │   ├── training.log
│   │   │   ├── metrics.json
│   │   │   └── config.yaml
│   │   └── 2024-02-01_run2/
│   └── evaluation/
│       ├── clinical_accuracy.json
│       ├── bias_evaluation.json
│       └── safety_tests.json
│
└── configs/                      # Training configurations
    ├── lora_config.yaml
    ├── data_prep_config.yaml
    ├── evaluation_config.yaml
    └── deployment_config.yaml
```

### Backup Locations

```bash
# Backup storage
/backup/training_data/
├── daily/                        # Daily incremental backups
│   ├── 2024-02-01/
│   ├── 2024-02-02/
│   └── latest -> 2024-02-06/
├── weekly/                       # Weekly full backups
│   ├── 2024-W05/
│   └── 2024-W06/
└── monthly/                      # Monthly archives
    ├── 2024-01/
    └── 2024-02/

# Offsite backup (cloud)
s3://medobsmind-training-backup/
├── incremental/
└── full/
```

### Database Storage

```sql
-- Training data metadata in PostgreSQL
training_data_registry
├── id: UUID
├── data_type: VARCHAR (textbook, guideline, case, feedback)
├── source: VARCHAR
├── file_path: TEXT
├── file_size: BIGINT
├── format: VARCHAR (pdf, json, jsonl, txt)
├── quality_score: FLOAT
├── sanitization_status: VARCHAR
├── created_at: TIMESTAMP
├── last_modified: TIMESTAMP
└── metadata: JSONB
```

---

## 🖥️ Admin Interface - Training Data Management

### 1. Training Data Dashboard

**URL:** `https://admin.medobsmind.ai/training-data`

**Features:**
- 📊 **Overview Statistics**
  - Total training examples: 50,342
  - Data sources: 15
  - Last update: 2024-02-06
  - Next training: Scheduled 2024-02-15
  - Storage used: 125 GB / 500 GB

- 📁 **Data Sources Table**
  ```
  ┌────────────────┬──────────┬───────────┬─────────┬──────────┐
  │ Source         │ Examples │ Size      │ Quality │ Status   │
  ├────────────────┼──────────┼───────────┼─────────┼──────────┤
  │ ICMR Guidelines│ 1,245    │ 2.3 GB    │ 98.5%   │ ✅ Active │
  │ AIIMS Protocols│ 876      │ 1.8 GB    │ 97.2%   │ ✅ Active │
  │ Clinical Cases │ 15,432   │ 45 GB     │ 95.8%   │ ✅ Active │
  │ User Feedback  │ 10,234   │ 8.5 GB    │ 92.1%   │ ✅ Active │
  │ Textbooks      │ 20,555   │ 65 GB     │ 99.1%   │ ✅ Active │
  │ Synthetic Data │ 2,000    │ 2 GB      │ 94.0%   │ ✅ Active │
  └────────────────┴──────────┴───────────┴─────────┴──────────┘
  ```

- 🔍 **Search & Filter**
  - Search by source, date, quality
  - Filter by data type, status
  - Sort by size, examples, quality

### 2. Data Location Viewer

**Access:** Click on any data source

**View Details:**
```json
{
  "data_source": {
    "name": "ICMR Sepsis Guidelines 2023",
    "type": "guideline",
    "file_locations": [
      {
        "path": "/data/training/raw/guidelines/icmr/sepsis_2023.pdf",
        "size": "2.3 MB",
        "format": "PDF",
        "created": "2023-12-15",
        "checksum": "sha256:a7f3c8d9e2b1..."
      },
      {
        "path": "/data/training/processed/instruction_tuning/icmr_sepsis_*.jsonl",
        "size": "850 KB",
        "format": "JSONL",
        "examples": 342,
        "created": "2024-01-10"
      }
    ],
    "backup_locations": [
      "/backup/training_data/weekly/2024-W06/icmr_sepsis_2023.pdf",
      "s3://medobsmind-backup/guidelines/icmr_sepsis_2023.pdf"
    ],
    "metadata": {
      "language": "English",
      "year": 2023,
      "authors": ["ICMR Task Force"],
      "pages": 156,
      "quality_verified": true,
      "sanitization_complete": true
    }
  }
}
```

**Actions Available:**
- 📥 Download original file
- 📄 View processed data
- 📊 View training examples
- ✏️ Edit metadata
- 🗑️ Delete (with confirmation)
- 🔄 Reprocess data
- 📋 Copy file path

### 3. Feedback Data Viewer

**URL:** `https://admin.medobsmind.ai/training-data/feedback`

**View Collected Feedback:**
```
Recent Feedback (Last 7 Days)
┌────────────┬───────────────────┬──────────────┬────────┬──────────┐
│ ID         │ Type              │ User         │ Rating │ Status   │
├────────────┼───────────────────┼──────────────┼────────┼──────────┤
│ FB-0001234 │ Clinical Correct. │ Dr. Sharma   │ ⭐⭐⭐⭐    │ Sanitized│
│ FB-0001235 │ Alert Outcome     │ Dr. Patel    │ ⭐⭐⭐⭐⭐   │ Sanitized│
│ FB-0001236 │ Model Performance │ Dr. Kumar    │ ⭐⭐⭐     │ Pending  │
└────────────┴───────────────────┴──────────────┴────────┴──────────┘

Click to view sanitized data location:
/data/training/raw/feedback/2024_Q1/sanitized/FB-0001234.json
```

**Feedback Details:**
```json
{
  "feedback_id": "FB-0001234",
  "type": "clinical_correction",
  "original_location": "/data/feedback/raw/FB-0001234_raw.json",
  "sanitized_location": "/data/training/raw/feedback/2024_Q1/sanitized/FB-0001234.json",
  "context": {
    "alert_type": "NEWS2_HIGH",
    "ai_suggestion": "Consider sepsis protocol",
    "doctor_correction": "Hypovolemic shock, responded to fluids",
    "outcome": "Improved without antibiotics"
  },
  "rating": 4,
  "quality_score": 0.95,
  "training_ready": true,
  "sanitization_log": {
    "pii_removed": ["patient_name", "mrn", "location"],
    "anonymized": ["patient_id", "doctor_id", "timestamp"],
    "verified": true
  }
}
```

### 4. File Browser

**URL:** `https://admin.medobsmind.ai/training-data/browser`

**Interactive File Tree:**
```
📁 /data/training/
  ├── 📁 raw/
  │   ├── 📁 medical_textbooks/
  │   │   ├── 📄 harrisons_chapter_01.pdf (2.5 MB)
  │   │   ├── 📄 harrisons_chapter_02.pdf (3.1 MB)
  │   │   └── 📄 metadata.json (12 KB)
  │   ├── 📁 guidelines/
  │   │   ├── 📁 icmr/
  │   │   │   ├── 📄 sepsis_2023.pdf (2.3 MB) ⬅️ Click to view
  │   │   │   └── 📄 cardiac_care.pdf (1.8 MB)
  │   │   └── 📁 aiims/
  │   └── 📁 feedback/
  │       └── 📁 2024_Q1/
  │           ├── 📁 raw/ (10,234 files)
  │           └── 📁 sanitized/ (10,150 files)
  └── 📁 processed/
      └── 📄 train.jsonl (458 MB, 50,342 examples)
```

**File Actions:**
- 👁️ View file contents
- 📥 Download
- 📋 Copy path
- ℹ️ Show metadata
- 🔍 Search within file
- 📊 Statistics

---

## 🛠️ Admin API Endpoints

### Training Data Locations API

```bash
# Get all training data locations
GET /api/v1/admin/training/data/locations

Response:
{
  "total_size": "125 GB",
  "total_examples": 50342,
  "locations": [
    {
      "path": "/data/training/raw/guidelines/icmr/sepsis_2023.pdf",
      "type": "guideline",
      "size": "2.3 MB",
      "examples_extracted": 342,
      "quality_score": 0.985
    },
    // ... more locations
  ]
}

# Get specific data source location
GET /api/v1/admin/training/data/locations/{source_id}

# Get feedback data locations
GET /api/v1/admin/training/feedback/locations
GET /api/v1/admin/training/feedback/locations?status=sanitized&date_from=2024-01-01

# Download training data
GET /api/v1/admin/training/data/download/{file_id}
# Returns file download

# View training example
GET /api/v1/admin/training/examples/{example_id}

Response:
{
  "example_id": "train_00123",
  "source": "ICMR Sepsis Guidelines",
  "source_location": "/data/training/raw/guidelines/icmr/sepsis_2023.pdf",
  "processed_location": "/data/training/processed/instruction_tuning/train.jsonl#123",
  "instruction": "Explain sepsis management protocol",
  "input": "Patient with fever, hypotension, tachycardia",
  "output": "Based on Surviving Sepsis Campaign guidelines...",
  "metadata": {
    "quality_score": 0.98,
    "verified": true,
    "language": "English"
  }
}
```

### Training Pipeline API

```bash
# Get training status
GET /api/v1/admin/training/status

Response:
{
  "current_model": "dsquaremedicalmodel-v1.1",
  "training_active": false,
  "last_training": {
    "started": "2024-02-01T10:00:00Z",
    "completed": "2024-02-01T18:30:00Z",
    "duration": "8h 30m",
    "examples_used": 50342,
    "final_loss": 0.23,
    "model_location": "/data/training/models/dsquaremedicalmodel/v1.1/"
  },
  "next_training": {
    "scheduled": "2024-02-15T02:00:00Z",
    "estimated_duration": "8-10 hours",
    "new_examples": 2,145
  }
}

# Trigger new training
POST /api/v1/admin/training/start
{
  "data_location": "/data/training/processed/instruction_tuning/",
  "config": "lora_default",
  "notify_on_complete": true
}

# View training logs
GET /api/v1/admin/training/logs/{run_id}

# Get data statistics
GET /api/v1/admin/training/data/stats

Response:
{
  "by_source": {
    "textbooks": 20555,
    "guidelines": 2121,
    "clinical_cases": 15432,
    "feedback": 10234,
    "synthetic": 2000
  },
  "by_quality": {
    "excellent": 48234,  // >95%
    "good": 1856,        // 85-95%
    "fair": 252          // 75-85%
  },
  "by_language": {
    "English": 45342,
    "Hindi": 3000,
    "Mixed": 2000
  },
  "storage": {
    "total": "125 GB",
    "raw": "85 GB",
    "processed": "35 GB",
    "models": "5 GB"
  }
}
```

---

## 📊 Data Quality Dashboard

**URL:** `https://admin.medobsmind.ai/training-data/quality`

### Quality Metrics

```
Data Quality Overview
┌─────────────────────┬──────────┬──────────┬──────────┐
│ Metric              │ Current  │ Target   │ Status   │
├─────────────────────┼──────────┼──────────┼──────────┤
│ Overall Quality     │ 96.8%    │ >95%     │ ✅ Good   │
│ Sanitization Rate   │ 99.2%    │ 100%     │ ⚠️ Review │
│ Completeness        │ 98.5%    │ >98%     │ ✅ Good   │
│ Accuracy (Clinical) │ 97.3%    │ >95%     │ ✅ Good   │
│ Bias Score          │ 0.12     │ <0.15    │ ✅ Good   │
│ Duplication Rate    │ 2.1%     │ <5%      │ ✅ Good   │
└─────────────────────┴──────────┴──────────┴──────────┘

Issues Detected:
• 8 files pending sanitization → /data/training/raw/feedback/pending/
• 12 examples with low quality score → Review recommended
• 3 duplicate entries → Deduplication suggested
```

### Quality Checks

```python
# Admin can trigger quality checks
POST /api/v1/admin/training/quality/check

Checks performed:
✅ PII detection (ensure no identifiers)
✅ Medical accuracy (expert review sample)
✅ Bias detection (demographic fairness)
✅ Duplication detection
✅ Format validation
✅ Completeness check
```

---

## 🔐 Access Control

### Admin Permissions

```python
# Only admins can access training data locations
@require_role("super_admin", "admin", "developer")
def view_training_data_location(file_id):
    """
    View exact file location of training data
    """
    file_info = get_file_info(file_id)
    
    # Log access for audit
    log_admin_action(
        user=current_user,
        action="view_training_data_location",
        resource=file_id,
        timestamp=now()
    )
    
    return {
        "file_path": file_info.path,
        "backup_paths": file_info.backup_paths,
        "metadata": file_info.metadata
    }
```

### Audit Trail

All admin actions on training data are logged:
```sql
admin_audit_log
├── timestamp: 2024-02-06 14:30:25
├── admin_user: sharmapank-j
├── action: view_training_data_location
├── resource: /data/training/raw/guidelines/icmr/sepsis_2023.pdf
├── ip_address: 192.168.1.100
└── details: "Viewed file location via admin dashboard"
```

---

## 📱 Mobile Admin App Access

### Android Admin App

**Feature:** View Training Data Locations

```kotlin
// Admin can view data locations on mobile
class TrainingDataActivity : AppCompatActivity() {
    fun viewDataLocations() {
        val response = adminApi.getTrainingDataLocations()
        
        // Display in list
        response.locations.forEach { location ->
            addLocationCard(
                path = location.path,
                size = location.size,
                examples = location.examples
            )
        }
    }
    
    fun downloadTrainingData(fileId: String) {
        // Download capability for admins
        adminApi.downloadFile(fileId)
    }
}
```

---

## 💾 Data Export

### Export Training Data

**URL:** `https://admin.medobsmind.ai/training-data/export`

**Options:**
```
Export Training Data

Format:
( ) JSONL (recommended)
( ) CSV
( ) Parquet

Filters:
☑ Include metadata
☑ Include quality scores
☐ Include raw sources
☑ Sanitized only

Date Range:
From: [2024-01-01] To: [2024-02-06]

Data Types:
☑ Guidelines
☑ Clinical cases
☑ Feedback
☐ Textbooks (large)

[Export] [Cancel]

Estimated size: 2.3 GB
Export location: /exports/training_data_2024-02-06.zip
```

---

## 🔄 Data Sync & Backup

### Backup Status Dashboard

**URL:** `https://admin.medobsmind.ai/training-data/backups`

```
Backup Status
┌─────────────┬──────────────────┬────────┬─────────┐
│ Type        │ Last Backup      │ Size   │ Status  │
├─────────────┼──────────────────┼────────┼─────────┤
│ Daily       │ 2024-02-06 02:00 │ 125 GB │ ✅ OK    │
│ Weekly      │ 2024-02-04 03:00 │ 125 GB │ ✅ OK    │
│ Monthly     │ 2024-02-01 04:00 │ 120 GB │ ✅ OK    │
│ Cloud (S3)  │ 2024-02-06 05:00 │ 125 GB │ ✅ OK    │
└─────────────┴──────────────────┴────────┴─────────┘

Next Scheduled Backups:
• Daily: Tonight at 02:00
• Weekly: Sunday at 03:00
• Cloud sync: Every 6 hours

Backup Locations:
• Local: /backup/training_data/
• NAS: //nas01/medobsmind_backup/
• Cloud: s3://medobsmind-training-backup/
```

---

## 📋 Quick Access Commands

### CLI Commands (Admin Terminal)

```bash
# View training data locations
medobsmind-admin data locations

# List all training examples
medobsmind-admin data list --source=feedback --limit=100

# View specific file
medobsmind-admin data view /data/training/raw/guidelines/icmr/sepsis_2023.pdf

# Download training data
medobsmind-admin data download --source=all --output=/tmp/training_export/

# Check data quality
medobsmind-admin data quality-check

# View training statistics
medobsmind-admin data stats

# Search training data
medobsmind-admin data search "sepsis management"

# Trigger training
medobsmind-admin training start --config=lora_default

# View training logs
medobsmind-admin training logs --run=latest
```

---

## 🎯 Summary for Admin (You)

### What You Can Do

1. **View All Data Locations**
   - Exact file paths for all training data
   - Raw and processed data
   - Backup locations
   - Cloud storage locations

2. **Access Training Data**
   - Download any training file
   - View processed examples
   - Browse feedback data
   - Export datasets

3. **Monitor Data Quality**
   - Quality scores
   - Sanitization status
   - Completeness checks
   - Bias detection

4. **Control Training**
   - Trigger new training runs
   - View training progress
   - Access training logs
   - Deploy new models

5. **Manage Backups**
   - View backup status
   - Restore from backups
   - Configure backup schedules

### Quick Access URLs

**For You (Admin):**
- Training Data Dashboard: `https://admin.medobsmind.ai/training-data`
- File Browser: `https://admin.medobsmind.ai/training-data/browser`
- Feedback Data: `https://admin.medobsmind.ai/training-data/feedback`
- Quality Dashboard: `https://admin.medobsmind.ai/training-data/quality`
- Training Control: `https://admin.medobsmind.ai/training/control`

### Security Notes

- ✅ Only you (super_admin) can access raw training data
- ✅ All access is logged for audit
- ✅ MFA required for data downloads
- ✅ IP whitelist enforced
- ✅ Data encrypted at rest and in transit

---

**Document Version:** 1.0  
**Last Updated:** 2024-02-06  
**Access Level:** Super Admin Only  
**Your Access:** ✅ Full Access Granted
