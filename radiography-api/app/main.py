from fastapi import FastAPI, UploadFile, File

from app.db.database import Base, engine
from app.routers.auth_router import router as auth_router
from app.routers.radiography_router import router as radiography_router
from app.services.cloudinary_service import upload_image
from app.routers.cloudinary_router import router as cloudinary_router


app = FastAPI(
    title="Radiography API",
    version="1.0.0"
)


@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        print(" Database initialized successfully")
    except Exception as e:
        print(" Database initialization failed:", e)



app.include_router(auth_router, prefix="/api/v1")
app.include_router(radiography_router, prefix="/api/v1/radiography")

app.include_router(cloudinary_router, prefix="/api/v1/cloudinary")


@app.get(
    "/",
    tags=["System"],
    summary="Health check",
    description="Verify that the API is running correctly"
)
def root():
    return {"message": "API is running"}

