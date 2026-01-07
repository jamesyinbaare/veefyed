import uvicorn
from fastapi import FastAPI, status
from typing import Any

app = FastAPI(title="My Skin Scanner")

@app.get("/", status_code=status.HTTP_200_OK)
def test() -> dict[str, Any]:
    return {"success": True, "service": "skin-scanner"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
