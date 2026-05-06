import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import JSONResponse
from PIL import Image

router = APIRouter(prefix="/uploads", tags=["uploads"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_SIZE = 1920
QUALITY = 85


@router.post("", status_code=status.HTTP_201_CREATED)
def upload_image(file: UploadFile = File(...)) -> dict[str, str]:
    if not file.content_type or not file.content_type.startswith("image/"):
        return JSONResponse(
            status_code=400,
            content={"error_code": "validation_error", "message": "Only image files are allowed."},
        )

    ext = _safe_extension(file.content_type)
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename

    try:
        image = Image.open(file.file)

        # Remove EXIF by creating a new image without info
        data = image.getdata()
        clean = Image.new(image.mode, image.size)
        clean.putdata(data)

        # Resize if too large
        if clean.width > MAX_SIZE or clean.height > MAX_SIZE:
            clean.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)

        # Save as JPEG to strip metadata and compress
        save_path = filepath if ext == ".jpg" else filepath.with_suffix(".jpg")
        if clean.mode in ("RGBA", "P"):
            clean = clean.convert("RGB")
        clean.save(save_path, format="JPEG", quality=QUALITY, optimize=True)

        # If we changed extension, remove the old path reference
        final_name = save_path.name

    except Exception as exc:
        return JSONResponse(
            status_code=400,
            content={"error_code": "validation_error", "message": f"Image processing failed: {exc}"},
        )
    finally:
        file.file.close()

    # Return the public URL path
    return {"url": f"/uploads/{final_name}"}


def _safe_extension(content_type: str) -> str:
    mapping = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    return mapping.get(content_type, ".jpg")
