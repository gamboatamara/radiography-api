from fastapi import FastAPI, UploadFile, File

from app.db.database import Base, engine
from app.routers.auth_router import router as auth_router
from app.routers.radiography_router import router as radiography_router
from app.services.cloudinary_service import upload_image

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Radiography API",
    version="1.0.0"
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(radiography_router, prefix="/api/v1/radiography", tags=["Radiography"])


@app.get("/")
def root():
    return {"message": "API is running"}


@app.post("/test-upload")
def test_upload(file: UploadFile = File(...)):
    url = upload_image(file)
    return {"url": url}