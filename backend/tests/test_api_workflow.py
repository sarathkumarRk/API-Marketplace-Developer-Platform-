def test_api_creation_requires_authentication(client):
    response = client.post(
        "/apis/",
        json={
            "organization_id": 1,
            "name": "Test API",
            "slug": "test-api-pytest",
            "description": "Test API",
            "category": "Testing",
            "status": "draft"
        }
    )

    assert response.status_code in [401, 403]


def test_api_approval_requires_admin(client):
    response = client.post(
        "/apis/1/approve"
    )

    assert response.status_code in [401, 403]


def test_api_publishing_requires_provider(client):
    response = client.post(
        "/apis/1/publish"
    )

    assert response.status_code in [401, 403, 400]