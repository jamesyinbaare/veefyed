from uuid import UUID

from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    image_id: UUID


class ImageAnalysisResponse(BaseModel):
    image_id: UUID
    skin_type: str
    issues: list[str]
    confidence: float


class ImageAnalysisRequest(BaseModel):
    image_id: UUID
