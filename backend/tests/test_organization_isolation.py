def test_organization_isolation(client):
    response = client.post(
        "/apis/",
        json={
            "organization_id": 999999,
            "name": "Unauthorized API",
            "slug": "unauthorized-api-pytest",
            "description": "Isolation test",
            "category": "Testing",
            "status": "draft"
        }
    )

    assert response.status_code in [401, 403]