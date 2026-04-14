from fastapi import APIRouter

router = APIRouter(prefix="/radiography", tags=["Radiography"])


@router.get("/test", 
    summary="Test radiography module",
    description="Simple endpoint to verify that the radiography module is working correctly.",
    responses={
        200: {"description": "Radiography module is working"}
    }
)
def test_radiography():
    return {"message": "Radiography funcionando"}
