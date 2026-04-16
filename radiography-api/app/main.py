from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.database import Base, engine
from app.routers.auth_router import router as auth_router
from app.routers.radiography_router import router as radiography_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully")
    except Exception as e:
        print("Database initialization failed:", e)
    
    yield

    print("Application shutting down")


app = FastAPI(
    title="Radiography API",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(auth_router, prefix="/api/v1")
app.include_router(radiography_router, prefix="/api/v1/radiography")


@app.get(
    "/",
    tags=["System"],
    summary="Health check",
    description="Verify that the API is running correctly"
)
def root():
    return {"message": "API is running"}