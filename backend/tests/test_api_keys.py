def test_api_key_requires_authentication(client):
    response = client.post(
        "/api-keys/",
        json={
            "developer_id": 1,
            "subscription_id": 1,
            "expires_at": None
        }
    )

    assert response.status_code in [401, 403]


def test_invalid_api_key(client):
    response = client.get(
        "/api-gateway/api/payments",
        headers={
            "X-API-Key": "invalid-api-key",
            "X-API-Version": "version1"
        }
    )

    assert response.status_code == 401


def test_expired_api_key(client):
    response = client.get(
        "/api-gateway/api/payments",
        headers={
            "X-API-Key": "expired-api-key",
            "X-API-Version": "version1"
        }
    )

    assert response.status_code == 401