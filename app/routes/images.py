import logging

from fastapi import APIRouter, File, UploadFile

from app.schemas.image import ImageUploadResponse

router = APIRouter(prefix="/api/v1/images", tags=["images"])

logger = logging.getLogger(__name__)


@router.post("/upload", summary="Upload an image")
async def upload_image(file: UploadFile = File(...)) -> ImageUploadResponse:
    logger.debug(f"Uploading image: {file.filename}")

    _ = await file.read()

    return ImageUploadResponse(image_id="12345")
