import os
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from ai_core.cloud.client import ovhai_initialize
from ai_core.tracking.client import mlflow_initialize
from app.datasets.views import router as datasets_router
from app.models.views import router as models_router
from app.jobs.views import router as jobs_router
from app.inference.views import router as inference_router
from app.experiments.views import router as experiments_router
from app.evaluate.views import router as evaluate_router
from app.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="ML HUB API", redirect_slashes=True)

# CORS in dev mode only
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "development":
    dev_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
        "http://127.0.0.1",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=dev_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS enabled for development")
else:
    logger.info("CORS disabled for production")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# Backend api routes at /api
api_router = APIRouter(prefix="/api")
api_router.include_router(datasets_router)
api_router.include_router(models_router)
api_router.include_router(jobs_router)
api_router.include_router(inference_router)
api_router.include_router(experiments_router)
api_router.include_router(evaluate_router)
app.include_router(api_router)


# Init ovhai cli
ovhai_initialize()

# Init mlflow
mlflow_initialize()

@app.get("/health")
def health_check():
    return {"message": "healthy"}

# Frontend routes at /
STATIC_DIR = os.getenv("STATIC_DIR", "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
