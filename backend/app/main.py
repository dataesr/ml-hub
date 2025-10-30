from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.ovhai import ovhai_initialize, router as ovhai_router
from app.hf import router as hf_router
from app.wandb import router as wandb_router

app = FastAPI(title="ML HUB BACKEND")

# Allow your React app to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(ovhai_router)
app.include_router(hf_router)
app.include_router(wandb_router)


# Init ovhai cli
ovhai_initialize()


@app.get("/")
def root():
    return {"message": "FastAPI backend is running!"}


@app.get("/health")
def health_check():
    return {"message": "healthy"}
