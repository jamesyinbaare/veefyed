import pytest
from httpx import AsyncClient

from app.dependencies.database import get_db_session
from app.config import settings


from uuid import uuid4

class FakeDBImage:
    def __init__(self, image_id, file_path: str):

        self.image_id = image_id
        self.file_path = file_path



@pytest.mark.asyncio
async def test_upload_valid_image(client: AsyncClient, override_db_session, fake_session_assign_uuid):
    # Use helper fixture to override DB session; assigns UUID on refresh
    override_db_session(fake_session_assign_uuid)

    files = {"file": ("test.jpg", b"\xff\xd8\xff", "image/jpeg")}

    response = await client.post("/api/v1/images/upload", files=files)

    assert response.status_code == 200
    payload = response.json()
    # returned image_id should be a UUID string
    assert payload.get("image_id") is not None


@pytest.mark.asyncio
async def test_upload_invalid_mime_type(client: AsyncClient, override_db_session, fake_session_noop):
    # Override DB session with no-op mock since this test only checks validation
    override_db_session(fake_session_noop)

    files = {"file": ("test.txt", b"hello", "text/plain")}
    response = await client.post("/api/v1/images/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]



@pytest.mark.asyncio
async def test_upload_file_too_large(client: AsyncClient, override_db_session, fake_session_noop):
    # Override DB session with no-op mock since this test only checks validation
    override_db_session(fake_session_noop)

    large_content = b"0" * (settings.storage_max_size + 1)
    files = {"file": ("big.jpg", large_content, "image/jpeg")}
    response = await client.post("/api/v1/images/upload", files=files)
    assert response.status_code == 400
    assert "File size exceeds" in response.json()["detail"]



@pytest.mark.asyncio
async def test_analyze_image_found(client: AsyncClient, mock_storage, override_db_session, fake_session_factory):
    uid = uuid4()


    stored_path = mock_storage.store(b"fake-image-bytes", "image.jpeg")

    # Override DB to return the pre-populated image record
    override_db_session(fake_session_factory(FakeDBImage(uid, stored_path)))

    response = await client.post("/api/v1/images/analyze", json={"image_id": str(uid)})

    assert response.status_code == 200
    payload = response.json()
    assert payload["image_id"] == str(uid)
    assert "skin_type" in payload
    assert isinstance(payload.get("issues"), list)
    assert isinstance(payload.get("confidence"), float)


@pytest.mark.asyncio
async def test_analyze_image_not_found(client: AsyncClient, override_db_session, fake_session_factory):
    uid = uuid4()

    # Return no DB record for this id
    override_db_session(fake_session_factory(None))

    response = await client.post("/api/v1/images/analyze", json={"image_id": str(uid)})

    assert response.status_code == 404
