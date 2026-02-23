# Copilot Instructions – AESI-MRP-PILOT

## Project Overview
**AESI-MRP-PILOT** (AI-Enhanced Safety Intelligence – Managed Response Platform) is a safety-triage system that:
1. Accepts user-submitted text describing potential safety incidents.
2. Routes that text through a domain-specific risk-pattern engine.
3. Produces a structured response (safe message, assigned responder, timeout) and optionally opens a Managed Response Protocol (MRP) case.

---

## Repository Layout

```
BACKEND-FASTAPI/
  domains/          # One file per safety domain
  routers/          # FastAPI route handlers
  services/         # Domain-routing orchestration
FRONTEND/
  src/
    components/
      enterprise/   # React/JSX UI components
.github/
  workflows/        # GitHub Actions CI
```

---

## Tech Stack

| Layer     | Technology                  |
|-----------|-----------------------------|
| Backend   | Python 3, FastAPI, Pydantic |
| Frontend  | React (JSX), plain CSS      |
| CI        | GitHub Actions              |

---

## Backend Architecture

### Domain Interface Contract
Every domain class in `BACKEND-FASTAPI/domains/` **must** implement these four static methods:

```python
@staticmethod
def get_risk_patterns() -> Dict[RiskTypeEnum, List[str]]:
    """Return a mapping of risk-type → list of lowercase keyword strings."""
    ...

@staticmethod
def get_safe_response(risk_type: RiskTypeEnum) -> str:
    """Return a user-facing safe-language response string for the given risk type."""
    ...

@staticmethod
def assign_responder(risk_type: RiskTypeEnum) -> str:
    """Return the identifier of the internal team/role that handles this risk type."""
    ...

@staticmethod
def get_timeout_minutes(risk_type: RiskTypeEnum) -> int:
    """Return how many minutes are allowed before escalation."""
    ...
```

Failure to implement any of these four methods will cause a runtime error in `DomainRouter.process_input()`.

### Adding a New Domain
1. Create `BACKEND-FASTAPI/domains/<name>.py`.
2. Define a risk-type enum class that inherits from both `str` and `Enum` (e.g. `class MyRiskType(str, Enum):`).
3. Implement the four static methods above (keyword lists must be **lowercase**).
4. Register the domain in `BACKEND-FASTAPI/services/domain_router.py`:
   ```python
   from domains.<name> import <DomainClass>
   DOMAIN_MAP = {
       ...
       "<name>": <DomainClass>,
   }
   ```
5. Add a corresponding POST endpoint in `BACKEND-FASTAPI/routers/enterprise_safety.py`.

### Risk Pattern Conventions
- Keyword strings in `get_risk_patterns()` are **lowercase**.
- `DomainRouter.process_input()` calls `.lower()` on both the incoming text and the keywords before matching, so casing in the source file is still normalised at runtime—but lowercase source strings are the established convention.

### Timeout Guidelines (existing domains)
| Urgency       | Minutes |
|---------------|---------|
| Immediate     | 5–15    |
| Elevated      | 60      |
| Standard      | 240     |

---

## Frontend Architecture

### Component Conventions
- Components live in `FRONTEND/src/components/enterprise/`.
- Files use `.jsx` extension with named exports (`export const ComponentName`).
- State is managed with React `useState` hooks; no Redux is currently used.
- API calls use `/api/enterprise/<slug>` where the URL slug is defined per domain (see table below) and may differ from the domain key.

#### Enterprise Domain Route Mapping

| Domain key      | URL slug        | Example endpoint                     |
|-----------------|-----------------|--------------------------------------|
| `public_safety` | `public-safety` | `/api/enterprise/public-safety`      |

When adding new domains, update this table with the correct slug so that frontend and backend stay aligned.
### API Request Shape
```json
{
  "text": "<user report>",
  "anonymous": true,
  "user_id": null,
  "location": "<optional>"
}
```

### Anonymous Reporting
When `anonymous: true` is set and the backend creates an MRP case, the response includes a `tracking_code` that the UI must display prominently and instruct the user to save.

---

## Coding Style

- **Python**: follow PEP 8; use type hints for all function signatures; define risk-type enumerations as `class RiskType(str, Enum):` so values are both string-comparable and enum-safe.
- **JavaScript/JSX**: functional components only; use `const`; accessibility attributes (`role`, `aria-*`) on interactive elements.
- Do not commit secrets, PII samples, or real personal data to the repository.

---

## CI / Testing

- GitHub Actions workflow is defined in `.github/workflows/blank.yml`.
- Before adding new backend logic, run existing tests (if present) with `pytest` from `BACKEND-FASTAPI/`.
- Frontend automated test tooling is not yet set up; once a `package.json` and test suite are added under `FRONTEND/`, update this section with the correct install and test commands.
