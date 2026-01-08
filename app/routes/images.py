import logging

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy import select

from app.config import settings
from app.dependencies.database import DBSessionDep
from app.models import Image
from app.schemas.image import ImageAnalysisRequest, ImageAnalysisResponse, ImageUploadResponse
from app.services.storage import storage_service

router = APIRouter(prefix="/api/v1/images", tags=["images"])

logger = logging.getLogger(__name__)


@router.post("/upload", summary="Upload an image")
async def upload_image(session: DBSessionDep, file: UploadFile = File(...)) -> ImageUploadResponse:
    allowed_mime_types = ["image/jpeg", "image/png"]
    if file.content_type not in allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed types: {', '.join(allowed_mime_types)}",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > settings.storage_max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.storage_max_size} bytes",
        )

    file_path, _ = await storage_service.save(content, file.filename or "unknown")
    db_image = Image(file_path=file_path, file_size=len(content), mime_type=file.content_type)
    session.add(db_image)
    await session.commit()
    await session.refresh(db_image)

    return ImageUploadResponse(image_id=db_image.image_id)


@router.post("/analyze", summary="Analyze an image")
async def get_image_metadata(req: ImageAnalysisRequest, session: DBSessionDep) -> ImageAnalysisResponse:
    stmt = select(Image).where(Image.image_id == req.image_id)
    result = await session.execute(stmt)
    db_image = result.scalar_one_or_none()
    if not db_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )

    try:
        _ = await storage_service.retrieve(db_image.file_path)
        logger.info(f"Analyzing image {req.image_id}")
        return ImageAnalysisResponse(
            image_id=db_image.image_id,
            skin_type="Oily",
            issues=["Hyperpigmentation"],
            confidence=0.87,
        )

    except Exception as e:
        logger.error(f"Error analyzing image {req.image_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing image",
        )
