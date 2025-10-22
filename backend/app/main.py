from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import routes

app = FastAPI(title="ML HUB BACKEND")

# Allow your React app to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(routes.router)


@app.get("/")
def root():
    return {"message": "FastAPI backend is running!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
