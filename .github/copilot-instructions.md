# Copilot Instructions for AESI-MRP-PILOT

## Project Overview

AESI-MRP-PILOT is an **Enterprise Multi-Domain Safety System** that detects risk signals in user-submitted text and routes cases to the appropriate responder. The system covers four safety domains: **workplace**, **public safety**, **commerce**, and **AI governance**.

## Repository Structure

```
├── BACKEND-FASTAPI/
│   ├── domains/         # One module per safety domain
│   ├── routers/         # FastAPI route handlers
│   └── services/        # Cross-domain orchestration (DomainRouter)
└── FRONTEND/
    └── src/
        └── components/
            └── enterprise/  # React components for safety forms
```

## Backend (Python / FastAPI)

### Domain Interface

Every domain class **must** implement these four static methods:

| Method | Return type | Purpose |
|---|---|---|
| `get_risk_patterns()` | `Dict[RiskType, List[str]]` | Keyword lists used for text matching |
| `get_safe_response(risk_type)` | `str` | Human-safe response message |
| `assign_responder(risk_type)` | `str` | Responder role/queue name |
| `get_timeout_minutes(risk_type)` | `int` | SLA response window in minutes |

Example skeleton for a new domain:

```python
class MyDomain:
    @staticmethod
    def get_risk_patterns() -> Dict[MyRiskType, List[str]]:
        return { MyRiskType.EXAMPLE: ["keyword one", "keyword two"] }

    @staticmethod
    def get_safe_response(risk_type: MyRiskType) -> str:
        ...

    @staticmethod
    def assign_responder(risk_type: MyRiskType) -> str:
        ...

    @staticmethod
    def get_timeout_minutes(risk_type: MyRiskType) -> int:
        ...
```

### Risk Patterns

- All keyword strings in `get_risk_patterns()` must be **lowercase**.
- Matching is case-insensitive (the router lowercases the input before comparison).

### Adding a New Domain

1. Create `BACKEND-FASTAPI/domains/<domain_name>.py` with a `RiskType` enum and a domain class.
2. Register the domain in `BACKEND-FASTAPI/services/domain_router.py` under `DomainRouter.DOMAIN_MAP`.
3. Add a corresponding FastAPI endpoint in `BACKEND-FASTAPI/routers/enterprise_safety.py`.

### Pydantic Models

- Request payloads use `BaseModel` subclasses defined at the top of the router file.
- Response payloads use `EnterpriseSafetyResponse` (or a domain-specific extension).

### Anonymous Reporting

- When `anonymous=True`, `AnonymousReportService.create_anonymous_case()` (in `domains/workplace.py`) generates an `anonymous_id` using **SHA-256** over a random 16-byte token combined with the current timestamp, then truncates to 16 hex characters. A separate URL-safe `tracking_code` is returned to the user for follow-up.
- Never log or persist raw user identity alongside anonymous cases.

## Frontend (React / JSX)

- Components live in `FRONTEND/src/components/enterprise/`.
- The `AnonymousReportForm` component maps `domain` prop values (`workplace`, `public_safety`, `commerce`) to backend API endpoints. The `ai_governance` domain is a system-to-system safety check (see `/api/enterprise/ai-safety-check`) and is **not** exposed through this user-facing form.
- API calls use `fetch` with `Content-Type: application/json`.
- Always handle `response.ok` before reading the JSON body.
- Display error messages in an element with `role="alert"` for accessibility.

## Coding Conventions

- **Python**: follow PEP 8; use type hints on all function signatures.
- **React**: functional components with hooks; `.jsx` extension.
- Keep domain logic inside `domains/`; keep HTTP concerns inside `routers/`.
- Do not import from `routers/` inside `domains/` or `services/`.
