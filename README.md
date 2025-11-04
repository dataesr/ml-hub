# ML-Hub

## Build

- Docker (Makefile): `make docker-build`

## Local development

- Docker Compose: `docker compose up --build`
- Backend: `pip install -r backend/requirements.txt && uvicorn app.main:app --reload --app-dir backend`
- Frontend: `cd frontend && npm ci && npm run dev`
