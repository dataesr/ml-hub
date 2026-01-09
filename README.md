# ML-Hub

## Build

- Docker (Makefile): `make docker-build`

## Local development

- All: `docker compose up --build -d`
- Backend: `docker compose build backend && docker compose up backend -d`
- Frontend: `cd frontend && npm ci && npm run dev`

---

## Repository Architecture

```
ml-hub/
├── libs/ai_core/       # Core ML library (shared logic)
├── app/
│   ├── backend/        # FastAPI REST API
│   └── frontend/       # React (Vite) web interface
└── docker/images/      # Docker images for cloud execution
```

### `libs/ai_core/` — Core Library

The `ai_core` library contains all the core ML logic, independent of the API layer. It is organized into modules:

- **`pipelines/`** — Pipeline registry, execution engine, schema builder
- **`cloud/`** — OVH AI client for managing jobs and apps
- **`tracking/`** — MLflow client for experiment tracking
- **`configs/`** — YAML config loading and management
- **`datasets/`** — Dataset utilities and preprocessing
- **`models/`** — Model utilities
- **`utils/`** — Shared helpers

This library can be used standalone (e.g., in scripts or notebooks) or through the API.

### `app/backend/` — REST API

A **FastAPI** application that exposes `ai_core` functionalities via HTTP endpoints. It handles request validation, routing, and serves as the interface between the frontend and the core library.

### `docker/images/` — Cloud Execution Images

Docker images used for running pipelines on OVH AI cloud:

- **`cuda-base`** — Base CUDA image with ai_core installed
- **`cuda-unsloth`** — Optimized image for Unsloth fine-tuning
- **`cuda-vllm`** — Image for vLLM inference
- **`mlflow`** — MLflow tracking server

---

### Pipelines

Create your ML pipelines in the `libs/ai_core/pipelines/pipelines/` folder using the pipeline registry decorator. Each pipeline defines its input schema, configuration, and execution logic. Once registered, pipelines become available through the API and can be executed either **locally** or on **OVH AI cloud infrastructure**. The execution mode is determined by the pipeline configuration.
See `examples/pipelines.ipynb` for how to use pipelines API.

### Experiment Tracking

All pipeline runs are automatically tracked via **MLflow** integration. The API provides access to experiment projects and their associated runs, allowing you to browse training metrics, compare model performance, and review logged artifacts. Each run captures parameters, metrics, and outputs for full reproducibility.

### Configurations

Store and manage reusable YAML configurations through the API. This includes prompt templates, training hyperparameters, model settings, and any other structured configuration your pipelines need. Configs are organized by type and can be loaded dynamically at runtime, making it easy to swap configurations without modifying code. (Not fully implemented yet)
