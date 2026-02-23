# Copilot Instructions

## Repository context
- Backend lives in `BACKEND-FASTAPI` (Python/FastAPI safety domains and router).
- Frontend lives in `FRONTEND/src` (React components).
- Workflow at `.github/workflows/blank.yml` only echoes messages today.

## Working style
- Keep changes minimal and localized; avoid unrelated refactors.
- Follow existing backend domain pattern methods (`get_risk_patterns`, `get_safe_response`, `assign_responder`, `get_timeout_minutes`) and keep risk keywords lowercase.
- Prefer existing dependencies/stdlib; avoid adding new packages unless required.
- Do not touch `.github/agents` or commit secrets; respect `.gitignore`.
- Stay ASCII unless a file already uses other characters.

## Testing and validation
- Backend tests live in `BACKEND-FASTAPI/tests/` and use `pytest`. Run them with:
  `DATABASE_URL=sqlite:///:memory: SECRET_KEY=test pytest tests/ -v`
  (requires `pip install -r requirements-dev.txt` first).
- For frontend changes, prefer React Testing Library. If tests are not run, state that explicitly.
- Manually sanity-check modified flows when possible and call out what was validated.

## Issue logging
- Keep a short running log of issues found and fixes applied in progress updates/PR description.
- Only fix issues within scope; note out-of-scope concerns separately.

## File-specific guidance
- Backend domain classes should remain small and rule-focused; avoid cross-domain coupling.
- Each domain class must implement the four-method interface: `get_risk_patterns()`, `get_safe_response()`, `assign_responder()`, `get_timeout_minutes()`.
- `AIGovernanceDomain` uses a `_CRITICAL_RISK_TYPES` class constant `(UNSAFE_OUTPUT, HARMFUL_INSTRUCTION, PRIVACY_LEAK, JAILBREAK_ATTEMPT)` to drive assignment, timeout, and action logic uniformly. Add new critical risk types there rather than duplicating the list across methods.
- Frontend components use functional React with hooks; keep state local and avoid adding global state unless necessary.
