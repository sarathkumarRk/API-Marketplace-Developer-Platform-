def test_usage_endpoint_requires_authentication(client):
    response = client.get(
        "/usage/my"
    )

    assert response.status_code in [401, 403]


def test_usage_analytics_requires_authentication(client):
    response = client.get(
        "/usage/analytics"
    )

    assert response.status_code in [401, 403]