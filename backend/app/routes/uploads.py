import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from ..config import settings
from ..security import require_admin

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


@router.post("/image", status_code=status.HTTP_201_CREATED)
def upload_image(file: UploadFile, _admin: str = Depends(require_admin)):
    extension = ALLOWED_TYPES.get(file.content_type)
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}",
        )

    images_dir = Path(settings.images_dir)
    images_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{extension}"
    destination = images_dir / filename
    with destination.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    return {"image_url": f"/static/images/{filename}"}
