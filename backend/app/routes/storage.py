from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from app.dependencies import get_current_user
from app.services.cloudinary_service import upload_file


router = APIRouter(
    prefix="/storage",
    tags=["Cloud Storage"]
)


@router.post("/upload")
async def upload_to_cloudinary(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    try:
        contents = await file.read()

        result = upload_file(
            contents,
            folder="api_marketplace"
        )

        return {
            "message": "File uploaded successfully",
            "file_name": file.filename,
            "file_url": result["url"],
            "public_id": result["public_id"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )