import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
import hashlib
import uuid
from pathlib import Path
from typing import Dict, Optional
from app.services.storage import storage_service
from app.dependencies.database import get_sessionmanager, initialize_db, get_db_session
from app.main import app


@pytest.fixture
def override_db_session():
    from app.main import app as _app

    def _set(override_func):
        _app.dependency_overrides[get_db_session] = override_func

    try:
        yield _set
    finally:
        _app.dependency_overrides.pop(get_db_session, None)


@pytest.fixture
def fake_session_assign_uuid():
    """Return an override function that assigns a UUID on refresh."""
    async def _override_get_db_session():
        class FakeSession:
            def add(self, obj):
                self._obj = obj

            async def commit(self):
                pass

            async def refresh(self, obj):
                obj.image_id = uuid.uuid4()

        yield FakeSession()

    return _override_get_db_session


@pytest.fixture
def fake_session_factory():
    """Factory that returns an override which returns `scalar_value` from `scalar_one_or_none`."""
    def _factory(scalar_value):
        async def _override_get_db_session():
            class FakeSession:
                async def execute(self, stmt):
                    class Result:
                        def scalar_one_or_none(inner):
                            return scalar_value

                    return Result()

            yield FakeSession()

        return _override_get_db_session

    return _factory


@pytest.fixture
def fake_session_noop():
    """Return a minimal no-op session override for tests that don't need database functionality."""
    async def _override_get_db_session():
        class FakeSession:
            def add(self, obj):
                pass

            async def commit(self):
                pass

            async def refresh(self, obj):
                pass

        yield FakeSession()

    return _override_get_db_session


@pytest_asyncio.fixture(scope="function")
async def client_base():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def client(client_base):
    try:
        async with initialize_db(get_sessionmanager()):
            yield client_base
    except Exception:
        # If database isn't configured in test environment, fall back to plain client
        yield client_base



class MockStorageBackend:

    def __init__(self) -> None:
        self._data: Dict[str, bytes] = {}
        self._checksums: Dict[str, str] = {}

    def _make_path(self, filename: str) -> str:
        ext = Path(filename or "").suffix
        return f"mock/{uuid.uuid4().hex}{ext}"

    def _checksum(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    async def save(self, file_content: bytes, filename: str) -> tuple[str, str]:
        path = self._make_path(filename)
        checksum = self._checksum(file_content)
        self._data[path] = file_content
        self._checksums[path] = checksum
        return path, checksum

    async def retrieve(self, file_path: str) -> bytes:
        try:
            return self._data[file_path]
        except KeyError as exc:
            raise FileNotFoundError(f"File not found: {file_path}") from exc

    async def exists(self, file_path: str) -> bool:
        return file_path in self._data

    async def delete(self, file_path: str) -> None:
        self._data.pop(file_path, None)
        self._checksums.pop(file_path, None)

    async def get_checksum(self, file_path: str) -> str:
        try:
            return self._checksums[file_path]
        except KeyError as exc:
            raise FileNotFoundError(f"File not found: {file_path}") from exc

    def store(self, content: bytes, filename: Optional[str] = "file") -> str:
        path = self._make_path(filename or "file")
        checksum = self._checksum(content)
        self._data[path] = content
        self._checksums[path] = checksum
        return path


@pytest.fixture(autouse=True)
def mock_storage():
    backend = MockStorageBackend()
    storage_service._backend = backend
    try:
        yield backend
    finally:
        storage_service._backend = None
