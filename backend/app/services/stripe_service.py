import stripe

from app.config import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(
    plan_name: str,
    plan_price: float,
    success_url: str,
    cancel_url: str,
    subscription_id: int
):
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[
            {
                "price_data": {
                    "currency": "inr",
                    "product_data": {
                        "name": plan_name
                    },
                    "unit_amount": int(plan_price * 100),
                    "recurring": {
                        "interval": "month"
                    }
                },
                "quantity": 1
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "subscription_id": str(subscription_id)
        },
        subscription_data={
            "metadata": {
                "subscription_id": str(subscription_id)
            }
        }
    )

    return session


def handle_stripe_webhook(
    payload: bytes,
    signature: str
):
    event = stripe.Webhook.construct_event(
        payload,
        signature,
        settings.STRIPE_WEBHOOK_SECRET
    )

    return event


def payment_successful(
    subscription_id: str
):
    return {
        "stripe_subscription_id": subscription_id,
        "status": "active"
    }


def payment_failed(
    subscription_id: str
):
    return {
        "stripe_subscription_id": subscription_id,
        "status": "payment_failed"
    }


def subscription_cancelled(
    subscription_id: str
):
    return {
        "stripe_subscription_id": subscription_id,
        "status": "cancelled"
    }


def subscription_renewed(
    subscription_id: str
):
    return {
        "stripe_subscription_id": subscription_id,
        "status": "active"
    }


def upgrade_subscription(
    subscription_id: str,
    price_id: str
):
    subscription = stripe.Subscription.retrieve(
        subscription_id
    )

    items = subscription["items"]["data"]

    if not items:
        raise ValueError(
            "Stripe subscription has no items"
        )

    item_id = items[0]["id"]

    return stripe.Subscription.modify(
        subscription_id,
        items=[
            {
                "id": item_id,
                "price": price_id
            }
        ]
    )


def downgrade_subscription(
    subscription_id: str,
    price_id: str
):
    subscription = stripe.Subscription.retrieve(
        subscription_id
    )

    items = subscription["items"]["data"]

    if not items:
        raise ValueError(
            "Stripe subscription has no items"
        )

    item_id = items[0]["id"]

    return stripe.Subscription.modify(
        subscription_id,
        items=[
            {
                "id": item_id,
                "price": price_id
            }
        ]
    )

