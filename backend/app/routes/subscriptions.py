from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import (
    get_current_user,
    developer_required,
    api_provider_required,
    platform_admin_required
)
from app.models.api import API
from app.models.api_plan import APIPlan
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.user import User
from app.models.webhook import Webhook
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse
)
from app.services.email_service import (
    send_subscription_activated_email,
    send_payment_failed_email,
    send_subscription_cancelled_email
)
from app.services.stripe_service import (
    create_checkout_session,
    handle_stripe_webhook,
    upgrade_subscription,
    downgrade_subscription
)
from app.routes.webhooks import deliver_webhook


router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"]
)


def trigger_webhook_event(
    db: Session,
    api_id: int,
    event_type: str,
    payload: dict,
    event_id: str | None = None
):
    webhooks = db.query(Webhook).filter(
        Webhook.api_id == api_id,
        Webhook.event_type == event_type,
        Webhook.is_active == True
    ).all()

    for webhook in webhooks:
        deliver_webhook(
            webhook=webhook,
            event_type=event_type,
            payload=payload,
            db=db,
            event_id=event_id
        )


@router.post(
    "/",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_subscription(
    data: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    if data.developer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create subscriptions for yourself"
        )

    api = db.query(API).filter(
        API.id == data.api_id,
        API.status == "published"
    ).first()

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Published API not found"
        )

    plan = db.query(APIPlan).filter(
        APIPlan.id == data.plan_id,
        APIPlan.api_id == data.api_id,
        APIPlan.is_active == True
    ).first()

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active API plan not found"
        )

    existing_subscription = db.query(Subscription).filter(
        Subscription.developer_id == current_user.id,
        Subscription.api_id == data.api_id,
        Subscription.status == "active"
    ).first()

    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active subscription already exists"
        )

    subscription = Subscription(
        developer_id=current_user.id,
        api_id=data.api_id,
        plan_id=data.plan_id,
        status="pending",
        started_at=None,
        expires_at=None
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    trigger_webhook_event(
        db=db,
        api_id=subscription.api_id,
        event_type="subscription.created",
        payload={
            "subscription_id": subscription.id,
            "developer_id": subscription.developer_id,
            "plan_id": subscription.plan_id,
            "status": subscription.status
        }
    )

    return subscription


@router.post(
    "/{subscription_id}/checkout"
)
def create_subscription_checkout(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.developer_id == current_user.id
    ).first()

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    if subscription.status not in [
        "pending",
        "payment_failed"
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Checkout is not available for this subscription"
        )

    plan = db.query(APIPlan).filter(
        APIPlan.id == subscription.plan_id,
        APIPlan.is_active == True
    ).first()

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active API plan not found"
        )

    if plan.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API plan price must be greater than 0"
        )

    try:
        session = create_checkout_session(
            plan_name=plan.name,
            plan_price=plan.price,
            success_url="http://localhost:5173/subscription/success",
            cancel_url="http://localhost:5173/subscription/cancel",
            subscription_id=subscription.id
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create Stripe checkout session"
        )

    return {
        "checkout_url": session.url,
        "session_id": session.id
    }


@router.get(
    "/my",
    response_model=list[SubscriptionResponse]
)
def get_my_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    subscriptions = db.query(Subscription).filter(
        Subscription.developer_id == current_user.id
    ).all()

    return subscriptions


@router.get(
    "/billing",
    response_model=list[SubscriptionResponse]
)
def get_my_billing(
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    subscriptions = db.query(Subscription).filter(
        Subscription.developer_id == current_user.id
    ).all()

    return subscriptions


@router.get(
    "/provider",
    response_model=list[SubscriptionResponse]
)
def get_provider_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(api_provider_required)
):
    organizations = db.query(Organization.id).filter(
        Organization.owner_id == current_user.id
    ).all()

    organization_ids = [
        organization[0]
        for organization in organizations
    ]

    if not organization_ids:
        return []

    apis = db.query(API.id).filter(
        API.organization_id.in_(organization_ids)
    ).all()

    api_ids = [
        api[0]
        for api in apis
    ]

    if not api_ids:
        return []

    subscriptions = db.query(Subscription).filter(
        Subscription.api_id.in_(api_ids)
    ).all()

    return subscriptions


@router.get(
    "/all",
    response_model=list[SubscriptionResponse]
)
def get_all_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(platform_admin_required)
):
    subscriptions = db.query(Subscription).all()

    return subscriptions


@router.get(
    "/{subscription_id}",
    response_model=SubscriptionResponse
)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id
    ).first()

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    if current_user.role == "developer":
        if subscription.developer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own subscriptions"
            )

        return subscription

    if current_user.role == "api_provider":
        api = db.query(API).filter(
            API.id == subscription.api_id
        ).first()

        if api is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API not found"
            )

        organization = db.query(Organization).filter(
            Organization.id == api.organization_id,
            Organization.owner_id == current_user.id
        ).first()

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view subscriptions for your own APIs"
            )

        return subscription

    if current_user.role == "platform_admin":
        return subscription

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


@router.post(
    "/{subscription_id}/cancel",
    response_model=SubscriptionResponse
)
def cancel_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.developer_id == current_user.id
    ).first()

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    if subscription.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active subscriptions can be cancelled"
        )

    if not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe subscription not found"
        )

    try:
        stripe.Subscription.cancel(
            subscription.stripe_subscription_id
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to cancel Stripe subscription"
        )

    return subscription


@router.post(
    "/{subscription_id}/upgrade",
    response_model=SubscriptionResponse
)
def upgrade_subscription_plan(
    subscription_id: int,
    price_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.developer_id == current_user.id
    ).first()

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    if subscription.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active subscriptions can be upgraded"
        )

    if not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe subscription not found"
        )

    try:
        upgrade_subscription(
            subscription.stripe_subscription_id,
            price_id
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to upgrade subscription"
        )

    return subscription


@router.post(
    "/{subscription_id}/downgrade",
    response_model=SubscriptionResponse
)
def downgrade_subscription_plan(
    subscription_id: int,
    price_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.developer_id == current_user.id
    ).first()

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    if subscription.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active subscriptions can be downgraded"
        )

    if not subscription.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe subscription not found"
        )

    try:
        downgrade_subscription(
            subscription.stripe_subscription_id,
            price_id
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to downgrade subscription"
        )

    return subscription


@router.post(
    "/stripe/webhook"
)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    payload = await request.body()

    signature = request.headers.get(
        "stripe-signature"
    )

    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe signature missing"
        )

    try:
        event = handle_stripe_webhook(
            payload,
            signature
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe webhook"
        )

    event_id = event.get("id")
    event_type = event.get("type")

    event_data = event.get(
        "data",
        {}
    ).get(
        "object",
        {}
    )

    if not event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Stripe event"
        )

    existing_subscription_id = event_data.get(
        "metadata",
        {}
    ).get(
        "subscription_id"
    )

    subscription = None

    if existing_subscription_id:
        try:
            subscription = db.query(
                Subscription
            ).filter(
                Subscription.id == int(
                    existing_subscription_id
                )
            ).first()

        except (ValueError, TypeError):
            subscription = None

    if subscription is None:
        stripe_subscription_id = event_data.get(
            "subscription"
        )

        if not stripe_subscription_id:
            stripe_subscription_id = event_data.get(
                "id"
            )

        if stripe_subscription_id:
            subscription = db.query(
                Subscription
            ).filter(
                Subscription.stripe_subscription_id ==
                stripe_subscription_id
            ).first()

    if subscription is None:
        return {
            "status": "ignored",
            "event_id": event_id
        }

    if event_type == "checkout.session.completed":
        stripe_subscription_id = event_data.get(
            "subscription"
        )

        if subscription.status == "active":
            return {
                "status": "already_processed",
                "event_id": event_id
            }

        if stripe_subscription_id:
            subscription.stripe_subscription_id = (
                stripe_subscription_id
            )

        subscription.status = "active"

        if subscription.started_at is None:
            subscription.started_at = datetime.now(
                timezone.utc
            )

        db.commit()
        db.refresh(subscription)

        developer = db.query(User).filter(
            User.id == subscription.developer_id
        ).first()

        if developer:
            send_subscription_activated_email(
                developer.email
            )

        trigger_webhook_event(
            db=db,
            api_id=subscription.api_id,
            event_type="payment.completed",
            payload={
                "subscription_id": subscription.id,
                "developer_id": subscription.developer_id,
                "stripe_subscription_id":
                    subscription.stripe_subscription_id,
                "status": subscription.status
            },
            event_id=event_id
        )

    elif event_type == "invoice.payment_failed":
        if subscription.status == "payment_failed":
            return {
                "status": "already_processed",
                "event_id": event_id
            }

        subscription.status = "payment_failed"

        db.commit()
        db.refresh(subscription)

        developer = db.query(User).filter(
            User.id == subscription.developer_id
        ).first()

        if developer:
            send_payment_failed_email(
                developer.email
            )

    elif event_type == "customer.subscription.deleted":
        if subscription.status == "cancelled":
            return {
                "status": "already_processed",
                "event_id": event_id
            }

        subscription.status = "cancelled"

        db.commit()
        db.refresh(subscription)

        developer = db.query(User).filter(
            User.id == subscription.developer_id
        ).first()

        if developer:
            send_subscription_cancelled_email(
                developer.email
            )

        trigger_webhook_event(
            db=db,
            api_id=subscription.api_id,
            event_type="subscription.cancelled",
            payload={
                "subscription_id": subscription.id,
                "developer_id": subscription.developer_id,
                "stripe_subscription_id":
                    subscription.stripe_subscription_id,
                "status": subscription.status
            },
            event_id=event_id
        )

    elif event_type == "customer.subscription.updated":
        if subscription.status != "active":
            subscription.status = "active"

            if subscription.started_at is None:
                subscription.started_at = datetime.now(
                    timezone.utc
                )

            db.commit()
            db.refresh(subscription)

    return {
        "status": "processed",
        "event_id": event_id
    }