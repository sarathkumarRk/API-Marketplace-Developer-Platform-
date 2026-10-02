def test_rate_limiting_requires_valid_request(client):
    response = client.get(
        "/api-gateway/api/payments",
        headers={
            "X-API-Key": "invalid-api-key",
            "X-API-Version": "version1"
        }
    )

    assert response.status_code == 401