import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.ovhai import ovhai_initialize, router as ovhai_router
from app.hf import router as hf_router
from app.wandb import router as wandb_router

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

# API routes under /api to coexist with SPA at /
api_router = APIRouter(prefix="/api")
api_router.include_router(ovhai_router)
api_router.include_router(hf_router)
api_router.include_router(wandb_router)
app.include_router(api_router)


# Init ovhai cli
ovhai_initialize()


# Health remains at /health; root is handled by SPA static files
@app.get("/health")
def health_check():
    return {"message": "healthy"}


STATIC_DIR = os.getenv("STATIC_DIR", "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
