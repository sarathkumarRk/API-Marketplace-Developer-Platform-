import cloudinary
import cloudinary.uploader

from app.config import settings


cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


def upload_file(file, folder="api_marketplace"):
    result = cloudinary.uploader.upload(
        file,
        folder=folder
    )

    return {
        "url": result.get("secure_url"),
        "public_id": result.get("public_id")
    }


def delete_file(public_id):
    return cloudinary.uploader.destroy(public_id)