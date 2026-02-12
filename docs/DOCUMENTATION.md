# AESI-MRP System Documentation

## Overview

The **AESI-MRP (Automated Escalation & Safety Intelligence - Mandatory Response Protocol)** system is a deterministic and auditable platform designed for handling high-risk signals with mandatory response enforcement.

## Architecture

### Core Components

1. **MRP Engine (`backend/mrp_engine.py`)**
   - Handles high-risk signal intake
   - Implements record locking with PENDING status
   - Manages 10-minute Responsibility Enforcement timer
   - Automatic escalation to Tier 2 supervisor on timeout
   - Intervention logging for record resolution

2. **Audit Log (`backend/audit_log.py`)**
   - Immutable audit trail with cryptographic hash chain
   - SQLite-based persistent storage
   - Tamper-evident logging for compliance
   - Chain integrity verification

3. **API (`backend/api.py`)**
   - FastAPI-based REST API
   - Endpoints for signal submission and intervention logging
   - Real-time status monitoring
   - Audit trail retrieval

4. **Dashboard (`frontend/dashboard.py`)**
   - Streamlit-based user interface
   - Fuzie Head interaction window for signal submission
   - Compliance Dashboard for PENDING alerts
   - Audit log viewer
   - System statistics

## Features

### 1. Signal Intake and Locking
When a high-risk signal is received:
- Record is immediately locked to `PENDING` status
- 10-minute timer starts automatically
- Event is logged to immutable audit trail
- Signal appears on Compliance Dashboard

### 2. Responsibility Enforcement
- 10-minute countdown timer per signal
- Visual time remaining indicator
- Staff must log intervention to unlock record
- Timer cannot be paused or reset

### 3. Automatic Escalation
If timer expires without intervention:
- Signal automatically escalates to `ESCALATED` status
- Tier 2 supervisor notification triggered
- Escalation event logged with timestamp
- No further intervention possible

### 4. Intervention Logging
Staff can log verified interventions:
- Action types: Parent Contacted, Student Counseling, Safety Check, etc.
- Staff ID required for accountability
- Optional notes for detailed documentation
- Immediate record unlock upon logging

### 5. Immutable Audit Trail
All actions are logged with:
- Cryptographic hash (SHA-256)
- Hash chain for tamper detection
- ISO 8601 timestamps
- Complete event data
- Chain integrity verification

## Installation

### Prerequisites
```bash
Python 3.8+
pip
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Backend API

```bash
# From project root
python -m backend.api
```

The API will be available at `http://localhost:8000`

### Starting the Dashboard

```bash
# From project root
streamlit run frontend/dashboard.py
```

The dashboard will open in your default browser.

## API Endpoints

### Signal Management

- `POST /api/signals/submit` - Submit a new high-risk signal
- `POST /api/signals/intervention` - Log an intervention
- `GET /api/signals/pending` - Get all PENDING signals
- `GET /api/signals/{signal_id}` - Get specific signal details
- `GET /api/signals` - Get all signals

### Audit Trail

- `GET /api/audit/{signal_id}` - Get audit trail for a signal
- `GET /api/audit` - Get recent audit entries
- `GET /api/audit/statistics` - Get audit log statistics

### System

- `GET /health` - Health check endpoint
- `GET /` - API information

## Testing

### Run Unit Tests
```bash
python -m pytest tests/test_mrp_engine.py -v
```

### Run API Tests
```bash
python -m pytest tests/test_api.py -v
```

### Run All Tests
```bash
python -m pytest tests/ -v
```

## Workflow Example

### 1. Signal Submission (Fuzie Head)
```json
POST /api/signals/submit
{
  "student_id": "STU-12345",
  "risk_type": "Behavioral Incident",
  "severity": "HIGH",
  "description": "Student exhibited concerning behavior",
  "detected_by": "AI Monitoring System"
}
```

**Response:**
```json
{
  "signal_id": "abc-123-def",
  "status": "PENDING",
  "message": "Signal received and locked. 10-minute timer started.",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. View on Compliance Dashboard
- Signal appears in PENDING alerts
- Timer countdown visible
- Staff can review details

### 3. Log Intervention
```json
POST /api/signals/intervention
{
  "signal_id": "abc-123-def",
  "action": "Parent Contacted",
  "staff_id": "STAFF-789",
  "notes": "Contacted parent, situation resolved"
}
```

**Response:**
```json
{
  "signal_id": "abc-123-def",
  "status": "RESOLVED",
  "message": "Intervention logged successfully. Signal unlocked."
}
```

### 4. Audit Trail
All events are automatically logged:
- `SIGNAL_RECEIVED` - Initial signal submission
- `INTERVENTION_LOGGED` - Staff intervention
- `ESCALATED_TO_TIER2` - Automatic escalation (if timeout)

## Security and Compliance

### Cryptographic Integrity
- Each audit entry hashed with SHA-256
- Hash chain prevents tampering
- Integrity verification available via API

### Deterministic Behavior
- Fixed 10-minute timer (non-configurable in production)
- Automatic escalation without human intervention
- Immutable audit trail

### Insurance Underwriter Requirements
- Complete audit trail for every action
- Cryptographic proof of non-tampering
- Deterministic escalation process
- Verifiable timestamps

## Configuration

### Timer Duration
Default: 10 minutes (600 seconds)

For testing purposes, modify in `backend/mrp_engine.py`:
```python
ESCALATION_TIMEOUT = 600  # seconds
```

### Database Location
Default: `audit_log.db` in project root

Configure in `backend/api.py`:
```python
audit_log = AuditLog(db_path="custom_path.db")
```

## Troubleshooting

### API Not Starting
- Ensure port 8000 is available
- Check if all dependencies are installed
- Verify Python version (3.8+)

### Dashboard Cannot Connect
- Ensure backend API is running
- Check API URL in `frontend/dashboard.py`
- Verify no firewall blocking localhost:8000

### Tests Failing
- Clean up any leftover `audit_log.db` files
- Ensure no other instance is using the test database
- Check Python path includes project root

## Project Structure

```
aesi-mrp-pilot/
├── backend/
│   ├── __init__.py
│   ├── mrp_engine.py       # Core MRP logic
│   ├── audit_log.py        # Immutable audit trail
│   └── api.py              # FastAPI endpoints
├── frontend/
│   └── dashboard.py        # Streamlit dashboard
├── tests/
│   ├── __init__.py
│   ├── test_mrp_engine.py  # Unit tests
│   └── test_api.py         # API integration tests
├── docs/
│   └── DOCUMENTATION.md    # This file
├── requirements.txt        # Python dependencies
├── README.md              # Project overview
└── .gitignore             # Git ignore rules
```

## License

See LICENSE file for details.

## Support

For issues or questions, please contact the development team.
