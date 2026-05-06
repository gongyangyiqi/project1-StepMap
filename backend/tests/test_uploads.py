import io
from pathlib import Path

from PIL import Image


def _make_image_bytes(fmt: str = "JPEG") -> bytes:
    img = Image.new("RGB", (100, 100), color="red")
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def test_upload_image_success(client):
    data = _make_image_bytes("JPEG")
    response = client.post(
        "/uploads",
        files={"file": ("test.jpg", io.BytesIO(data), "image/jpeg")},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["url"].startswith("/uploads/")
    assert payload["url"].endswith(".jpg")


def test_upload_png_converted_to_jpg(client):
    data = _make_image_bytes("PNG")
    response = client.post(
        "/uploads",
        files={"file": ("test.png", io.BytesIO(data), "image/png")},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["url"].endswith(".jpg")


def test_upload_non_image_rejected(client):
    response = client.post(
        "/uploads",
        files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["error_code"] == "validation_error"


def test_uploaded_file_is_accessible(client):
    data = _make_image_bytes("JPEG")
    upload = client.post(
        "/uploads",
        files={"file": ("test.jpg", io.BytesIO(data), "image/jpeg")},
    )
    url = upload.json()["url"]
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"


def test_upload_large_image_is_resized(client):
    img = Image.new("RGB", (3000, 3000), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    response = client.post(
        "/uploads",
        files={"file": ("huge.jpg", io.BytesIO(buf.getvalue()), "image/jpeg")},
    )
    assert response.status_code == 201
    url = response.json()["url"]
    # Verify the saved image is resized
    image_response = client.get(url)
    saved = Image.open(io.BytesIO(image_response.content))
    assert saved.width <= 1920
    assert saved.height <= 1920
