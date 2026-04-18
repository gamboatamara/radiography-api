from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

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


BASE_DIR = Path(__file__).resolve().parents[1]
GOOGLE_LOGIN_TEST_FILE = BASE_DIR / "google_login_test.html"


@app.get(
    "/",
    tags=["System"],
    summary="Health check",
    description="Verify that the API is running correctly"
)
def root():
    return {"message": "API is running"}


@app.get(
    "/google-login-test",
    tags=["System"],
    summary="Google login test page",
    description="Serve the Google login test page over HTTP instead of file://",
)
def google_login_test():
    return FileResponse(GOOGLE_LOGIN_TEST_FILE)
