from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import assets, employees, assignments, test

app = FastAPI(
    title="Asset Management API",
    description="API for managing office assets and employee assignments",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(assets.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(assignments.router, prefix="/api")
app.include_router(test.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Asset Management API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

