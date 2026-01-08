from typing import Any

import uvicorn
from fastapi import FastAPI, status

from app.routes import images

app = FastAPI(title="My Skin Scanner")

app.include_router(images.router)


@app.get("/", status_code=status.HTTP_200_OK)
def test() -> dict[str, Any]:
    return {"success": True, "service": "skin-scanner"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
