import pytest


@pytest.fixture()
def auth_client(client):
    client.post(
        "/auth/register",
        json={"email": "tripuser@example.com", "password": "password123"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "tripuser@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


def test_create_trip_success(auth_client):
    response = auth_client.post(
        "/trips",
        json={
            "title": "日本之旅",
            "start_date": "2024-03-01",
            "end_date": "2024-03-10",
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == "日本之旅"
    assert payload["start_date"] == "2024-03-01"
    assert payload["end_date"] == "2024-03-10"
    assert "id" in payload


def test_create_trip_invalid_date_range(auth_client):
    response = auth_client.post(
        "/trips",
        json={
            "title": "错误日期",
            "start_date": "2024-03-10",
            "end_date": "2024-03-01",
        },
    )
    assert response.status_code == 422


def test_list_trips_empty(auth_client):
    response = auth_client.get("/trips")
    assert response.status_code == 200
    assert response.json() == []


def test_list_trips_with_data(auth_client):
    auth_client.post(
        "/trips",
        json={"title": "旅行A", "start_date": "2024-01-01", "end_date": "2024-01-05"},
    )
    auth_client.post(
        "/trips",
        json={"title": "旅行B", "start_date": "2024-02-01", "end_date": "2024-02-05"},
    )

    response = auth_client.get("/trips")
    assert response.status_code == 200
    trips = response.json()
    assert len(trips) == 2
    assert trips[0]["title"] == "旅行B"  # 按创建时间倒序


def test_get_trip_detail(auth_client):
    create = auth_client.post(
        "/trips",
        json={"title": "详情测试", "start_date": "2024-01-01", "end_date": "2024-01-05"},
    )
    trip_id = create.json()["id"]

    response = auth_client.get(f"/trips/{trip_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "详情测试"
    assert payload["footprint_count"] == 0


def test_get_trip_not_found(auth_client):
    response = auth_client.get("/trips/99999")
    assert response.status_code == 404


def test_delete_trip_success(auth_client):
    create = auth_client.post(
        "/trips",
        json={"title": "待删除", "start_date": "2024-01-01", "end_date": "2024-01-05"},
    )
    trip_id = create.json()["id"]

    delete = auth_client.delete(f"/trips/{trip_id}")
    assert delete.status_code == 204

    get = auth_client.get(f"/trips/{trip_id}")
    assert get.status_code == 404


def test_trip_isolation_between_users(client):
    # User A
    client.post("/auth/register", json={"email": "usera@example.com", "password": "password123"})
    login_a = client.post("/auth/login", json={"email": "usera@example.com", "password": "password123"})
    token_a = login_a.json()["access_token"]

    # User B
    client.post("/auth/register", json={"email": "userb@example.com", "password": "password123"})
    login_b = client.post("/auth/login", json={"email": "userb@example.com", "password": "password123"})
    token_b = login_b.json()["access_token"]

    # User A creates trip
    headers_a = {"Authorization": f"Bearer {token_a}"}
    create = client.post(
        "/trips",
        json={"title": "私密旅行", "start_date": "2024-01-01", "end_date": "2024-01-05"},
        headers=headers_a,
    )
    trip_id = create.json()["id"]

    # User B tries to access
    headers_b = {"Authorization": f"Bearer {token_b}"}
    response = client.get(f"/trips/{trip_id}", headers=headers_b)
    assert response.status_code == 404


def test_create_trip_unauthorized(client):
    response = client.post(
        "/trips",
        json={"title": "未授权", "start_date": "2024-01-01", "end_date": "2024-01-05"},
    )
    assert response.status_code == 401
