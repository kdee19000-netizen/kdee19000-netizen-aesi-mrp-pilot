# AESI MRP – Frontend

React-based UI for the AI-Enhanced Safety Intelligence Mandatory Reporting Platform.

## Tech Stack

- **React 18** – functional components with hooks
- **Fetch API** – HTTP requests to the FastAPI backend

## Project Structure

```
FRONTEND/
└── src/
    └── components/
        └── enterprise/
            └── AnonymousReportForm.jsx   # Confidential report submission form
```

## Components

### `AnonymousReportForm`

Props:

| Prop     | Type   | Description                                          |
|----------|--------|------------------------------------------------------|
| `domain` | string | Safety domain: `workplace`, `public_safety`, `commerce` |

Features:
- Toggle anonymous submission (identity hashed server-side)
- Displays a one-time tracking code after anonymous submission
- Inline error messages on API failure

## Running Locally

```bash
npm install
npm start
```

The app expects the FastAPI backend to be running at the same origin (proxied via `package.json` `proxy` field or a reverse proxy).

## Backend API Endpoints

| Method | Path                              | Domain          |
|--------|-----------------------------------|-----------------|
| POST   | `/api/enterprise/workplace`       | Workplace HR    |
| POST   | `/api/enterprise/public-safety`   | Public Safety   |
| POST   | `/api/enterprise/commerce`        | E-Commerce      |
| POST   | `/api/enterprise/ai-safety-check` | AI Governance   |

See `BACKEND-FASTAPI/README.md` for full request/response schemas.
