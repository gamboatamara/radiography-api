from fastapi import FastAPI
from app.routers.auth_router import router as auth_router
from app.routers.radiography_router import router as radiography_router

app = FastAPI(
    title="Radiography API",
    version="1.0.0"
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(radiography_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "API is running"}
