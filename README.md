# AESI-MRP Pilot MVP

**Automated Escalation & Safety Intelligence - Mandatory Response Protocol**

## 🎯 Overview

The **AESI-MRP Pilot MVP** is a deterministic and auditable system for handling high-risk signals with mandatory response enforcement. Built for insurance underwriter compliance, the system ensures every action is logged with cryptographic timestamps and provides automatic escalation for unhandled signals.

## ✨ Key Features

### 1. Core MRP Engine
- ✅ **High-Risk Signal Intake**: Receive and process critical safety signals
- 🔒 **Automatic Record Locking**: Immediate PENDING status on signal receipt
- ⏱️ **10-Minute Enforcement Timer**: Countdown for mandatory response
- 📝 **Intervention Logging**: Staff can log verified actions to unlock records
- 🚨 **Automatic Escalation**: Tier 2 escalation on timer expiry

### 2. Immutable Audit Trail
- 🔐 **Cryptographic Hash Chain**: SHA-256 hashing for tamper detection
- 📊 **Complete Event Logging**: Every action tracked with timestamps
- ✓ **Chain Integrity Verification**: Verify audit log hasn't been tampered with
- 💾 **SQLite Persistence**: Reliable local storage

### 3. REST API
- 🚀 **FastAPI Backend**: High-performance async API
- 📡 **RESTful Endpoints**: Standard HTTP methods for all operations
- 📖 **Auto-Generated Docs**: Swagger UI at `/docs`
- 🔍 **Real-Time Status**: Monitor all signals and their states

### 4. Interactive Dashboard
- 🤖 **Fuzie Head Interface**: Submit new high-risk signals
- 📊 **Compliance Dashboard**: View all PENDING alerts with timer countdowns
- 📜 **Audit Log Viewer**: Browse complete audit trail
- 📈 **System Statistics**: Monitor system health and integrity

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/kdee19000-netizen/kdee19000-netizen-aesi-mrp-pilot.git
cd kdee19000-netizen-aesi-mrp-pilot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Start the system**

**Option A: Using the startup script (Unix/Linux/Mac)**
```bash
chmod +x start.sh
./start.sh
```

**Option B: Manual startup**

Terminal 1 - Start Backend API:
```bash
python -m backend.api
```

Terminal 2 - Start Dashboard:
```bash
streamlit run frontend/dashboard.py
```

4. **Access the system**
- **Dashboard**: Opens automatically in browser (usually http://localhost:8501)
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📖 Usage

### Submitting a High-Risk Signal

1. Navigate to **Fuzie Head Interaction** page
2. Fill in the signal details:
   - Student ID
   - Risk Type (Behavioral Incident, Safety Concern, etc.)
   - Severity (HIGH or CRITICAL)
   - Description
   - Detected By (source of detection)
3. Click **Submit High-Risk Signal**
4. The system will:
   - Lock the record to PENDING
   - Start the 10-minute timer
   - Log the event to audit trail
   - Display on Compliance Dashboard

### Logging an Intervention

1. Navigate to **Compliance Dashboard**
2. Find the PENDING signal
3. Select the intervention action (e.g., "Parent Contacted")
4. Enter your Staff ID
5. Add optional notes
6. Click **Log Intervention**
7. The system will:
   - Unlock the record (RESOLVED)
   - Stop the escalation timer
   - Log the intervention to audit trail

### Viewing Audit Trail

1. Navigate to **Audit Log** page
2. Select a specific signal or view all entries
3. Expand entries to see:
   - Event type
   - Timestamp
   - Cryptographic hash
   - Complete event data

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Streamlit Dashboard                 │
│  (Fuzie Head + Compliance Dashboard + Audit Viewer) │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP/REST
                      ▼
┌─────────────────────────────────────────────────────┐
│                   FastAPI Backend                    │
│            (REST API + Request Handling)             │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
┌───────────────────┐     ┌──────────────────┐
│   MRP Engine      │     │   Audit Log      │
│                   │────▶│                  │
│ • Signal Intake   │     │ • Hash Chain     │
│ • Timer Logic     │     │ • Immutability   │
│ • Escalation      │     │ • Verification   │
└───────────────────┘     └──────────────────┘
```

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Unit Tests Only
```bash
python -m pytest tests/test_mrp_engine.py -v
```

### Run API Tests Only
```bash
python -m pytest tests/test_api.py -v
```

## 📁 Project Structure

```
aesi-mrp-pilot/
├── backend/
│   ├── __init__.py
│   ├── mrp_engine.py       # Core MRP logic with timer & escalation
│   ├── audit_log.py        # Immutable audit trail with hash chain
│   └── api.py              # FastAPI REST endpoints
├── frontend/
│   └── dashboard.py        # Streamlit dashboard UI
├── tests/
│   ├── __init__.py
│   ├── test_mrp_engine.py  # Unit tests for MRP engine
│   └── test_api.py         # Integration tests for API
├── docs/
│   └── DOCUMENTATION.md    # Comprehensive documentation
├── requirements.txt        # Python dependencies
├── start.sh               # Startup script
├── README.md              # This file
└── .gitignore
```

## 🔐 Security & Compliance

### Cryptographic Integrity
- **SHA-256 Hashing**: Each audit entry includes a cryptographic hash
- **Hash Chain**: Entries linked via previous hash for tamper detection
- **Verification API**: `/api/audit/statistics` provides chain validation

### Deterministic Behavior
- **Fixed Timer**: 10-minute window cannot be paused or extended
- **Automatic Escalation**: No human intervention in escalation logic
- **Immutable Logs**: Audit entries cannot be modified or deleted

### Insurance Underwriter Requirements
- ✅ Complete audit trail for every action
- ✅ Cryptographic proof of non-tampering
- ✅ Deterministic escalation process
- ✅ Verifiable ISO 8601 timestamps
- ✅ Clear accountability (Staff IDs logged)

## 📚 API Documentation

### Signal Endpoints
- `POST /api/signals/submit` - Submit new high-risk signal
- `POST /api/signals/intervention` - Log intervention
- `GET /api/signals/pending` - Get PENDING signals
- `GET /api/signals/{signal_id}` - Get signal details
- `GET /api/signals` - Get all signals

### Audit Endpoints
- `GET /api/audit/{signal_id}` - Get audit trail for signal
- `GET /api/audit` - Get recent audit entries
- `GET /api/audit/statistics` - Get statistics & verify integrity

### System Endpoints
- `GET /health` - Health check
- `GET /` - API information

Full API documentation with interactive testing: http://localhost:8000/docs

## 🤝 Contributing

This is a pilot MVP system. For feature requests or bug reports, please open an issue.

## 📄 License

See LICENSE file for details.

## 📞 Support

For detailed documentation, see [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md)