from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.routers.auth_router import router as auth_router
from app.routers.radiography_router import router as radiography_router

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOOGLE_LOGIN_TEST_FILE = PROJECT_ROOT / "google_login_test.html"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Schema management is handled externally via Alembic migrations.
    # Run: alembic upgrade head
    print(
        "Startup ready: expecting database schema to be migrated via Alembic"
    )

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


@app.get(
    "/google-login-test",
    tags=["System"],
    summary="Google login test page",
    description=(
        "Serve a simple page to test Google Sign-In and retrieve an ID token"
    ),
)
def google_login_test():
    html = GOOGLE_LOGIN_TEST_FILE.read_text(encoding="utf-8")
    html = html.replace("__GOOGLE_CLIENT_ID__", settings.GOOGLE_CLIENT_ID)
    return HTMLResponse(content=html)