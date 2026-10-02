def test_gateway_requires_api_key(client):
    response = client.get(
        "/api-gateway/api/payments",
        headers={
            "X-API-Version": "version1"
        }
    )

    assert response.status_code == 401


def test_gateway_requires_api_version(client):
    response = client.get(
        "/api-gateway/api/payments",
        headers={
            "X-API-Key": "invalid-api-key"
        }
    )

    assert response.status_code == 401


def test_subscription_validation(client):
    response = client.get(
        "/api-gateway/api/payments",
        headers={
            "X-API-Key": "invalid-api-key",
            "X-API-Version": "version1"
        }
    )

    assert response.status_code == 401


def test_api_gateway_invalid_endpoint(client):
    response = client.get(
        "/api-gateway/api/invalid-endpoint",
        headers={
            "X-API-Key": "invalid-api-key",
            "X-API-Version": "version1"
        }
    )

    assert response.status_code == 401