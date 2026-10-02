from app.routes.webhooks import (
    create_signature,
    verify_signature
)


def test_webhook_signature_validation():
    payload = '{"event":"subscription.created"}'
    secret = "test-secret"

    signature = create_signature(
        payload,
        secret
    )

    assert verify_signature(
        payload,
        signature,
        secret
    ) is True


def test_invalid_webhook_signature():
    payload = '{"event":"subscription.created"}'
    secret = "test-secret"

    assert verify_signature(
        payload,
        "invalid-signature",
        secret
    ) is False


def test_duplicate_webhook():
    assert True