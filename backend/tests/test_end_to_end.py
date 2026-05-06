import io
from datetime import datetime, timezone

from PIL import Image


def _make_image() -> io.BytesIO:
    img = Image.new("RGB", (100, 100), color="green")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


def test_full_journey_register_create_trip_add_footprint(client):
    """
    End-to-end test covering the complete V1.0 core flow:
    Register -> Login -> Create Trip -> Upload Image -> Add Footprint ->
    View Trip Detail -> View Timeline -> View Map Data
    """

    # 1. Register
    reg = client.post(
        "/auth/register",
        json={"email": "e2e@example.com", "password": "password123"},
    )
    assert reg.status_code == 201

    # 2. Login
    login = client.post(
        "/auth/login",
        json={"email": "e2e@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})

    # 3. Verify /auth/me
    me = client.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "e2e@example.com"

    # 4. Create Trip
    trip_res = client.post(
        "/trips",
        json={
            "title": "端到端测试旅行",
            "start_date": "2024-06-01",
            "end_date": "2024-06-07",
        },
    )
    assert trip_res.status_code == 201
    trip_id = trip_res.json()["id"]

    # 5. List trips (should contain the new trip)
    trips = client.get("/trips")
    assert trips.status_code == 200
    assert len(trips.json()) == 1
    assert trips.json()[0]["footprint_count"] == 0

    # 6. Upload image
    upload = client.post(
        "/uploads",
        files={"file": ("photo.jpg", _make_image(), "image/jpeg")},
    )
    assert upload.status_code == 201
    image_url = upload.json()["url"]

    # 7. Add footprint
    footprint_res = client.post(
        "/footprints",
        json={
            "trip_id": trip_id,
            "image_url": image_url,
            "note": "这是一次端到端测试的足迹",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "location_name": "东京",
            "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
    )
    assert footprint_res.status_code == 201
    footprint_id = footprint_res.json()["id"]

    # 8. View trip detail (footprint count should be updated)
    detail = client.get(f"/trips/{trip_id}")
    assert detail.status_code == 200
    assert detail.json()["footprint_count"] == 1

    # 9. View timeline
    timeline = client.get(f"/footprints/trip/{trip_id}")
    assert timeline.status_code == 200
    fps = timeline.json()
    assert len(fps) == 1
    assert fps[0]["note"] == "这是一次端到端测试的足迹"
    assert fps[0]["image_url"] == image_url

    # 10. View map data
    map_data = client.get("/footprints/map")
    assert map_data.status_code == 200
    assert len(map_data.json()) == 1

    # 11. Verify uploaded image is accessible
    img_get = client.get(image_url)
    assert img_get.status_code == 200

    # 12. Delete trip (should cascade delete footprint)
    delete = client.delete(f"/trips/{trip_id}")
    assert delete.status_code == 204

    # 13. Verify trip is gone
    get_deleted = client.get(f"/trips/{trip_id}")
    assert get_deleted.status_code == 404

    # 14. Verify timeline is empty after trip deletion
    timeline_after = client.get(f"/footprints/trip/{trip_id}")
    assert timeline_after.status_code == 404


def test_unauthorized_access_is_blocked(client):
    """Verify that unauthenticated users cannot access protected resources."""

    # No token provided
    assert client.get("/trips").status_code == 401
    assert client.post("/trips", json={"title": "x", "start_date": "2024-01-01", "end_date": "2024-01-02"}).status_code == 401
    assert client.get("/footprints/map").status_code == 401
    assert client.get("/auth/me").status_code == 401

    # Invalid token
    client.headers.update({"Authorization": "Bearer invalid-token"})
    assert client.get("/trips").status_code == 401


def test_user_isolation_end_to_end(client):
    """Verify that users cannot see or modify each other's data."""

    # User A
    client.post("/auth/register", json={"email": "usera@example.com", "password": "password123"})
    login_a = client.post("/auth/login", json={"email": "usera@example.com", "password": "password123"})
    token_a = login_a.json()["access_token"]

    # User B
    client.post("/auth/register", json={"email": "userb@example.com", "password": "password123"})
    login_b = client.post("/auth/login", json={"email": "userb@example.com", "password": "password123"})
    token_b = login_b.json()["access_token"]

    # User A creates a trip
    client.headers.update({"Authorization": f"Bearer {token_a}"})
    trip = client.post(
        "/trips",
        json={"title": "私密", "start_date": "2024-01-01", "end_date": "2024-01-02"},
    )
    trip_id = trip.json()["id"]

    # User B cannot see User A's trip
    client.headers.update({"Authorization": f"Bearer {token_b}"})
    trips = client.get("/trips")
    assert trips.status_code == 200
    assert len(trips.json()) == 0

    # User B cannot access User A's trip detail
    detail = client.get(f"/trips/{trip_id}")
    assert detail.status_code == 404

    # User B cannot add footprint to User A's trip
    fp = client.post(
        "/footprints",
        json={
            "trip_id": trip_id,
            "image_url": "/uploads/test.jpg",
            "note": "hacked",
            "latitude": 0,
            "longitude": 0,
            "recorded_at": "2024-01-01T00:00:00Z",
        },
    )
    assert fp.status_code == 404
