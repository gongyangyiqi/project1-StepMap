def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"email": "User@Example.com", "password": "password123"},
    )
    assert response.status_code == 201
    payload = response.json()
    assert "id" in payload
    assert payload["email"] == "user@example.com"
    assert "created_at" in payload
    assert "password_hash" not in payload


def test_register_duplicate_email_returns_409(client):
    first = client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "password123"},
    )
    assert first.status_code == 201

    second = client.post(
        "/auth/register",
        json={"email": "dup@example.com", "password": "password123"},
    )
    assert second.status_code == 409
    payload = second.json()
    assert payload["error_code"] == "resource_error"
    assert "already" in payload["message"].lower()


def test_register_invalid_payload_returns_422(client):
    response = client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": "short"},
    )
    assert response.status_code == 422
    payload = response.json()
    assert payload["error_code"] == "validation_error"
    assert payload["message"]

