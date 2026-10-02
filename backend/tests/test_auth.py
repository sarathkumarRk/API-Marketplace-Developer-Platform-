import uuid


def test_registration(client):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": email,
            "password": "Test@123"
        }
    )

    assert response.status_code == 201
    assert "user_id" in response.json()


def test_login(client):
    email = f"login_{uuid.uuid4().hex[:8]}@example.com"
    password = "Test@123"

    register_response = client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_role_authorization(client):
    response = client.get(
        "/organizations/"
    )

    assert response.status_code in [401, 403]