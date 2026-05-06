def test_login_success(client):
    # Register first
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "password123"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "access_token" in payload
    assert payload["token_type"] == "bearer"


def test_login_invalid_password_returns_401(client):
    client.post(
        "/auth/register",
        json={"email": "login2@example.com", "password": "password123"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "login2@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    payload = response.json()
    assert payload["error_code"] == "auth_error"


def test_login_nonexistent_user_returns_401(client):
    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "password123"},
    )
    assert response.status_code == 401
    payload = response.json()
    assert payload["error_code"] == "auth_error"


def test_me_endpoint_with_valid_token(client):
    reg = client.post(
        "/auth/register",
        json={"email": "me@example.com", "password": "password123"},
    )
    assert reg.status_code == 201

    login = client.post(
        "/auth/login",
        json={"email": "me@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "me@example.com"


def test_me_endpoint_without_token_returns_401(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    payload = response.json()
    assert payload["error_code"] == "auth_error"
