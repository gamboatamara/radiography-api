from fastapi import FastAPI
from app.routers.auth_router import router as auth_router
from app.routers.radiography_router import router as radiography_router
from fastapi import UploadFile, File
from app.services.cloudinary_service import upload_image
from fastapi import FastAPI, UploadFile, File

app = FastAPI(
    title="Radiography API",
    version="1.0.0"
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(radiography_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "API funcionando"}

@app.post("/test-upload")
def test_upload(file: UploadFile = File(...)):
    url = upload_image(file)
    return {"url": url}