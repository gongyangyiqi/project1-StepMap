import pytest
from datetime import datetime, timezone


@pytest.fixture()
def auth_client(client):
    client.post(
        "/auth/register",
        json={"email": "fpuser@example.com", "password": "password123"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "fpuser@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture()
def sample_trip(auth_client):
    response = auth_client.post(
        "/trips",
        json={"title": "测试旅行", "start_date": "2024-01-01", "end_date": "2024-01-05"},
    )
    return response.json()["id"]


def test_create_footprint_success(auth_client, sample_trip):
    response = auth_client.post(
        "/footprints",
        json={
            "trip_id": sample_trip,
            "image_url": "https://example.com/photo.jpg",
            "note": "美丽的风景",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "location_name": "东京",
            "recorded_at": "2024-01-02T10:00:00Z",
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["note"] == "美丽的风景"
    assert payload["latitude"] == 35.6762
    assert payload["trip_id"] == sample_trip


def test_create_footprint_invalid_coords(auth_client, sample_trip):
    response = auth_client.post(
        "/footprints",
        json={
            "trip_id": sample_trip,
            "image_url": "https://example.com/photo.jpg",
            "note": "测试",
            "latitude": 999,
            "longitude": 139.6503,
            "recorded_at": "2024-01-02T10:00:00Z",
        },
    )
    assert response.status_code == 422


def test_list_footprints_by_trip(auth_client, sample_trip):
    auth_client.post(
        "/footprints",
        json={
            "trip_id": sample_trip,
            "image_url": "https://example.com/1.jpg",
            "note": "第一条足迹",
            "latitude": 35.0,
            "longitude": 139.0,
            "recorded_at": "2024-01-02T10:00:00Z",
        },
    )
    auth_client.post(
        "/footprints",
        json={
            "trip_id": sample_trip,
            "image_url": "https://example.com/2.jpg",
            "note": "第二条足迹",
            "latitude": 36.0,
            "longitude": 140.0,
            "recorded_at": "2024-01-03T12:00:00Z",
        },
    )

    response = auth_client.get(f"/footprints/trip/{sample_trip}")
    assert response.status_code == 200
    footprints = response.json()
    assert len(footprints) == 2
    assert footprints[0]["note"] == "第二条足迹"  # 按时间倒序


def test_footprint_trip_isolation(auth_client, sample_trip, client):
    auth_client.post(
        "/footprints",
        json={
            "trip_id": sample_trip,
            "image_url": "https://example.com/1.jpg",
            "note": "私密足迹",
            "latitude": 35.0,
            "longitude": 139.0,
            "recorded_at": "2024-01-02T10:00:00Z",
        },
    )

    # Another user
    client.post("/auth/register", json={"email": "other@example.com", "password": "password123"})
    login = client.post("/auth/login", json={"email": "other@example.com", "password": "password123"})
    token = login.json()["access_token"]

    response = client.get(
        f"/footprints/trip/{sample_trip}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_map_footprints(auth_client, sample_trip):
    auth_client.post(
        "/footprints",
        json={
            "trip_id": sample_trip,
            "image_url": "https://example.com/1.jpg",
            "note": "地图足迹",
            "latitude": 35.0,
            "longitude": 139.0,
            "recorded_at": "2024-01-02T10:00:00Z",
        },
    )

    response = auth_client.get("/footprints/map")
    assert response.status_code == 200
    footprints = response.json()
    assert len(footprints) == 1
    assert footprints[0]["note"] == "地图足迹"
