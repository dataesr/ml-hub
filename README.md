# ML-Hub

## Build

- Docker (Makefile): `make docker-build`

## Local development

- All: `docker compose up --build -d`
- Backend: `docker compose build backend && docker compose up backend -d`
- Frontend: `cd frontend && npm ci && npm run dev`
