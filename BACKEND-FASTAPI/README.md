# AESI-MRP FastAPI Backend – Quantum-Resilient

A production-ready FastAPI backend with **post-quantum cryptography (PQC)** for the AESI-MRP system.

## Features

| Feature | Status |
|---|---|
| FastAPI REST + WebSocket | ✅ |
| Post-Quantum signatures (Dilithium3) | ✅ |
| Hybrid classical RSA-4096 + PQ crypto | ✅ |
| Immutable audit chain with hash linking | ✅ |
| 10-minute MRP timer workflow | ✅ |
| PostgreSQL with SQLAlchemy ORM | ✅ |
| Redis caching and Celery workers | ✅ |
| Docker / docker-compose | ✅ |
| JWT authentication | ✅ |
| Rate limiting | ✅ |
| CORS middleware | ✅ |
| Multi-language support | ✅ |
| Parent portal API | ✅ |
| Prometheus-ready monitoring | ✅ |
| Alembic database migrations | ✅ |
| Comprehensive test suite | ✅ |

## Quick Start

### 1. Clone & configure

```bash
cp .env.example .env
# Edit .env with your database / API credentials
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### 3. Run locally (development)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Apply database migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload
```

## Directory Structure

```
BACKEND-FASTAPI/
├── main.py               – FastAPI app factory
├── dependencies.py       – DB session dependency
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── models/               – SQLAlchemy ORM models
├── schemas/              – Pydantic request/response schemas
├── services/             – Business logic (crypto, audit, MRP …)
├── routers/              – FastAPI route handlers
├── middleware/           – Auth, audit logging, rate limiting
├── workers/              – Celery background tasks
├── utils/                – Shared helpers
├── tests/                – pytest test suite
└── alembic/              – Database migrations
```

## API Endpoints

### Risk Management
| Method | Path | Description |
|---|---|---|
| POST | `/api/risk/signal` | Submit a risk signal (starts MRP timer) |
| POST | `/api/risk/intervention` | Staff intervention on a risk record |
| GET | `/api/risk/{id}` | Retrieve a risk record |

### Audit
| Method | Path | Description |
|---|---|---|
| GET | `/api/audit/proof/{id}` | Quantum-verified chain integrity proof |
| GET | `/api/audit/chain/{id}` | Full ordered audit chain |

### MRP
| Method | Path | Description |
|---|---|---|
| POST | `/api/mrp/run` | Trigger an MRP calculation run |
| GET | `/api/mrp/run/{id}` | Get MRP run status and results |

### Inventory
| Method | Path | Description |
|---|---|---|
| GET | `/api/inventory/` | List inventory items |
| POST | `/api/inventory/` | Create an inventory item |
| GET | `/api/inventory/{id}` | Get an item |
| PATCH | `/api/inventory/{id}` | Update an item |

### Parent Portal
| Method | Path | Description |
|---|---|---|
| GET | `/api/parent/{parent_id}/records` | Records linked to a parent |
| GET | `/api/parent/{parent_id}/records/{id}` | Specific record |

### Admin
| Method | Path | Description |
|---|---|---|
| POST | `/api/admin/users` | Create a user |
| GET | `/api/admin/users/{id}` | Get a user |
| GET | `/api/admin/stats` | System statistics |

### Real-time
| Protocol | Path | Description |
|---|---|---|
| WebSocket | `/ws/mrp/{run_id}` | Real-time MRP run updates |

## Running Tests

```bash
cd BACKEND-FASTAPI
pip install -r requirements.txt
pytest tests/ -v
```

## Post-Quantum Cryptography

The system uses a **hybrid signature scheme**:

1. **Classical**: RSA-4096 with PSS padding and SHA-512
2. **Post-Quantum**: Dilithium3 via the `oqs-python` library (Open Quantum Safe)

If `oqs-python` is not installed, the system falls back to RSA-only signatures
(v1 format) while logging a warning. The audit chain remains valid in both modes.

## Security

- 🔒 Quantum-resistant cryptography (Dilithium3 + RSA-4096)
- 🔒 Immutable audit chain with cryptographic hash linking
- 🔒 Signature verification before every audit commit
- 🔒 JWT authentication on protected routes
- 🔒 Sliding-window rate limiting
- 🔒 CORS protection
- 🔒 SQL injection prevention (SQLAlchemy ORM)
- 🔒 Pydantic input validation

## License

See the root [LICENSE](../LICENSE) file.
