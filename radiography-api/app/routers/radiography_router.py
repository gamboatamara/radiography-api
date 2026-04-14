from fastapi import APIRouter

router = APIRouter(prefix="/radiography", tags=["Radiography"])


@router.get("/test")
def test_radiography():
    return {"message": "Radiography funcionando"}
