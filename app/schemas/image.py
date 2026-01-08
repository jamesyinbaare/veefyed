from uuid import UUID

from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    image_id: UUID
