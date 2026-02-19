# GitHub Copilot Instructions for AESI-MRP-PILOT

## Project Overview
The **AESI-MRP-PILOT** (AI Enterprise Safety Intake - Multi-Risk Platform Pilot) is a multi-domain safety intake and risk assessment system. It provides automated routing and response coordination for workplace incidents, public safety concerns, e-commerce fraud, and AI governance issues.

**Core Purpose**: Route safety reports to appropriate responders based on pattern-matched risk analysis across four domains: workplace safety, public safety, commerce safety, and AI governance.

## Tech Stack

### Backend
- **Framework**: Python FastAPI (async/await)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic BaseModel
- **Python Version**: 3.8+

### Frontend
- **Framework**: React (functional components with hooks)
- **State Management**: Local component state with useState
- **HTTP Client**: Native Fetch API
- **Component Pattern**: Functional components (.jsx files)

### Infrastructure
- **CI/CD**: GitHub Actions
- **Version Control**: Git/GitHub

## Project Structure

```
BACKEND-FASTAPI/
├── domains/          # Domain-specific business logic and pattern matching
│   ├── ai_governance.py     # AI safety: bias, jailbreak, hallucinations
│   ├── workplace.py         # HR: harassment, discrimination, threats
│   ├── public_safety.py     # Crisis: abuse, homelessness, endangerment
│   └── commerce.py          # Trust & safety: fraud, scams, account takeover
├── routers/          # FastAPI endpoint definitions
│   └── enterprise_safety.py # Main API with 4 POST endpoints
└── services/         # Core routing and orchestration
    └── domain_router.py     # Central dispatcher for domain handlers

FRONTEND/
└── src/
    └── components/
        └── enterprise/
            └── AnonymousReportForm.jsx  # Anonymous reporting UI
```

## Commands

### Backend Development
Currently no build/test infrastructure is configured. When adding:
- Install dependencies: `pip install -r requirements.txt` (to be created)
- Run server: `uvicorn main:app --reload` (main.py to be created)
- Run tests: `pytest` (when tests are added)
- Lint: `flake8 BACKEND-FASTAPI/` or `black BACKEND-FASTAPI/` (when configured)

### Frontend Development
Currently no build/test infrastructure is configured. When adding:
- Install dependencies: `npm install` (package.json to be created)
- Start dev server: `npm start`
- Build: `npm run build`
- Run tests: `npm test` (when tests are added)
- Lint: `npm run lint` (when configured)

## Code Style and Conventions

### Python Code Style
```python
# Use async def for FastAPI endpoints
@router.post("/api/enterprise/workplace")
async def handle_workplace_safety(
    input_data: WorkplaceInput,
    db: Session = Depends(get_db)
):
    # Implementation
    pass

# Use Pydantic models for validation
class WorkplaceInput(BaseModel):
    message: str
    anonymous: bool = False
    contact_info: Optional[str] = None

# Use type hints consistently
from typing import Dict, List, Optional

def analyze_risk(input_text: str) -> Dict[str, any]:
    # Implementation
    pass

# Domain interface - all domain classes must implement:
# - get_risk_patterns() -> Dict[DomainEnumType, List[str]]
# - get_safe_response(risk_type) -> str
# - assign_responder(risk_type) -> str
# - get_timeout_minutes(risk_type) -> int
```

### React Code Style
```jsx
// Use functional components with hooks
import React, { useState } from 'react';

const ComponentName = () => {
  const [state, setState] = useState(initialValue);

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Implementation
  };

  return (
    <div className="component-name">
      {/* JSX */}
    </div>
  );
};

export default ComponentName;
```

### Naming Conventions
- **Python files**: `snake_case.py`
- **Python classes**: `PascalCase`
- **Python functions/variables**: `snake_case`
- **React components**: `PascalCase.jsx`
- **React functions/variables**: `camelCase`
- **CSS classes**: `kebab-case`
- **Constants**: `UPPER_SNAKE_CASE`

## Domain-Specific Patterns

### Risk Pattern Matching
All domain `get_risk_patterns()` methods must return lowercase string keyword lists keyed by a domain-specific `Enum` type:
```python
def get_risk_patterns(self) -> Dict[SomeDomainRiskType, List[str]]:
    return {
        SomeDomainRiskType.THREAT: ["threat", "weapon", "harm"],
        SomeDomainRiskType.HARASSMENT: ["harassment", "discrimination", "retaliation"],
        SomeDomainRiskType.HOSTILE: ["hostile", "unfair", "unsafe"]
    }
```

### Domain Handler Interface
Every domain class in `domains/` must implement these four methods:
1. `get_risk_patterns()` - Returns `Dict[DomainEnumType, List[str]]` risk-type-to-keyword mapping
2. `get_safe_response(risk_type)` - Returns confirmation message for the given risk type
3. `assign_responder(risk_type)` - Returns responder type string
4. `get_timeout_minutes(risk_type)` - Returns SLA timeout in minutes

Reference: `BACKEND-FASTAPI/services/domain_router.py:44,58-60`

### Anonymous Reporting
When handling anonymous reports:
- Generate anonymous ID using `hashlib.sha256` with `secrets.token_hex(16)` + timestamp
- Generate user-facing tracking code using `secrets.token_urlsafe(16)`
- Store hashed identifier instead of raw contact info
- Return tracking code in response for follow-up
- Pattern in `FRONTEND/src/components/enterprise/AnonymousReportForm.jsx`

## Testing Strategy

**Current Status**: No testing infrastructure exists yet.

When adding tests:
- **Python Backend**: Use `pytest` for unit and integration tests
  - Test each domain handler independently
  - Mock database sessions with `pytest-mock`
  - Test pattern matching with various input cases
  - Verify responder assignment logic

- **React Frontend**: Use `jest` and React Testing Library
  - Test component rendering
  - Test form submission flows
  - Test anonymous toggle behavior
  - Mock API calls with `jest.fn()`

- **Integration Tests**: Test full API flow from frontend to backend
  - Use Cypress or Playwright for E2E tests
  - Validate all four API endpoints
  - Test error handling paths

## Git Workflow

### Branch Naming
- Feature: `feature/description`
- Bug fix: `fix/description`
- Documentation: `docs/description`
- CI/CD: `ci/description`

### Commit Messages
Use conventional commits format:
- `feat: add new feature`
- `fix: resolve bug`
- `docs: update documentation`
- `refactor: restructure code`
- `test: add tests`
- `chore: maintenance tasks`

### Pull Requests
- Create descriptive PR titles
- Include summary of changes
- Reference related issues with `#issue-number`
- Ensure all endpoints still function
- Update this file if project structure changes

## Boundaries and Restrictions

### DO NOT
- **Never commit secrets or API keys** to the repository
- **Never modify domain interface methods** without updating all domain classes
- **Never change pattern matching** without testing against existing use cases
- **Never skip input validation** on API endpoints
- **Never remove anonymity features** from reporting flows
- **Never expose raw contact information** in anonymous reports
- **Do not touch** `.github/agents/` directory (reserved for other agent instructions)

### DO
- **Always use async/await** for FastAPI endpoints
- **Always validate input** with Pydantic models
- **Always implement all four methods** when creating new domain handlers
- **Always use lowercase** for risk pattern keywords
- **Always hash identifiers** for anonymous tracking
- **Always preserve existing API contracts** when refactoring
- **Always add type hints** to Python functions

## File Modification Guidelines

### When modifying domain files (`BACKEND-FASTAPI/domains/*.py`)
- Ensure all four required methods remain implemented
- Keep pattern keywords lowercase
- Test pattern matching with sample inputs
- Update `domain_router.py` if adding new domains

### When modifying API endpoints (`BACKEND-FASTAPI/routers/enterprise_safety.py`)
- Maintain existing endpoint paths
- Preserve Pydantic validation models
- Keep async pattern for all endpoints
- Test with actual HTTP requests

### When modifying frontend (`FRONTEND/src/components/enterprise/AnonymousReportForm.jsx`)
- Preserve anonymous reporting toggle
- Keep tracking code generation logic
- Maintain integration with all three safety endpoints
- Test form submission and error handling

## Security Considerations

### Input Validation
- All user input must pass through Pydantic validation
- Pattern matching provides basic content filtering
- Consider adding rate limiting for production

### Data Privacy
- Anonymous reports use hashed identifiers only
- Anonymous IDs are SHA-256 hashes (internal, not shown to users)
- User-facing tracking codes use `secrets.token_urlsafe(16)` (not SHA-256)
- Contact info is optional and handled carefully

### API Security
- Authentication/authorization not yet implemented
- Consider adding JWT or OAuth before production
- Database connections are stubbed (implement secure connection pooling)

## Deployment Notes

**Current Status**: No deployment infrastructure configured.

When setting up deployment:
- Create `main.py` entrypoint for FastAPI
- Add `requirements.txt` for Python dependencies
- Add `package.json` for React dependencies
- Configure environment variables for secrets
- Set up proper database connections
- Add Docker configuration if containerizing
- Update `.github/workflows/` with CI/CD pipelines

## Future Development Priorities

Based on current gaps:
1. **Add testing infrastructure** (pytest, jest, React Testing Library)
2. **Add linting/formatting** (black, flake8, ESLint, Prettier)
3. **Create build scripts** (requirements.txt, package.json, Makefile)
4. **Implement database layer** (actual SQLAlchemy models and migrations)
5. **Add authentication** (JWT tokens, OAuth integration)
6. **Add API documentation** (OpenAPI/Swagger via FastAPI)
7. **Set up logging** (structured logging for audit trails)
8. **Add monitoring** (health checks, metrics endpoints)

## Questions or Issues?

When working on this repository:
- Reference the domain interface requirements before modifying domains
- Check existing pattern matching before adding new keywords
- Verify API endpoint contracts before making breaking changes
- Test anonymous reporting flows to ensure privacy is maintained
- Consult the team before adding new dependencies or changing tech stack
