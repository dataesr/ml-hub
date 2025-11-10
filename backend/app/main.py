import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.ovhai import ovhai_initialize
from app.datasets.views import router as datasets_router
from app.models.views import router as models_router
from app.jobs.views import router as jobs_router
from app.inference.views import router as inference_router
from app.experiments.views import router as experiments_router

app = FastAPI(title="ML HUB API")

# Allow your React app to call the API
dev_origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost", "http://127.0.0.1"]
allow_origins = os.getenv("CORS_ORIGINS") or dev_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Backend api routes at /api
api_router = APIRouter(prefix="/api")
api_router.include_router(datasets_router)
api_router.include_router(models_router)
api_router.include_router(jobs_router)
api_router.include_router(inference_router)
api_router.include_router(experiments_router)
app.include_router(api_router)


# Init ovhai cli
ovhai_initialize()

@app.get("/health")
def health_check():
    return {"message": "healthy"}

# Frontend routes at /
STATIC_DIR = os.getenv("STATIC_DIR", "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
