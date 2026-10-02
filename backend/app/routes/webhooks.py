import hashlib
import hmac
import json
import time
import uuid

from datetime import datetime, timezone

import httpx

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import (
    get_current_user,
    api_provider_required
)

from app.models.api import API
from app.models.organization import Organization
from app.models.user import User
from app.models.webhook import Webhook
from app.models.webhook_delivery import WebhookDelivery

from app.schemas.webhook import (
    WebhookCreate,
    WebhookResponse,
    WebhookDeliveryResponse
)


router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"]
)


MAX_RETRIES = 3


def create_signature(payload: str, secret: str):
    return hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()


def verify_signature(
    payload: str,
    signature: str,
    secret: str
):
    expected_signature = create_signature(
        payload,
        secret
    )

    return hmac.compare_digest(
        expected_signature,
        signature
    )


def deliver_webhook(
    webhook: Webhook,
    event_type: str,
    payload: dict,
    db: Session,
    event_id: str | None = None
):
    """
    Deliver webhook with:

    - Unique event ID
    - Duplicate event protection
    - HMAC SHA256 signature
    - Retry mechanism
    - Delivery status tracking
    """

    if event_id is None:
        event_id = str(uuid.uuid4())

    # -------------------------------------------------
    # DUPLICATE EVENT CHECK
    # -------------------------------------------------

    existing_delivery = db.query(
        WebhookDelivery
    ).filter(
        WebhookDelivery.webhook_id == webhook.id,
        WebhookDelivery.event_id == event_id
    ).first()

    if existing_delivery:
        return existing_delivery

    # -------------------------------------------------
    # CREATE DELIVERY RECORD
    # -------------------------------------------------

    delivery = WebhookDelivery(
        webhook_id=webhook.id,
        event_id=event_id,
        status="pending",
        response_code=None,
        attempt_count=0,
        delivered_at=None
    )

    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    # -------------------------------------------------
    # WEBHOOK PAYLOAD
    # -------------------------------------------------

    payload_data = {
        "event_id": event_id,
        "event_type": event_type,
        "data": payload
    }

    payload_json = json.dumps(
        payload_data,
        separators=(",", ":"),
        default=str
    )

    # -------------------------------------------------
    # CREATE SIGNATURE
    # -------------------------------------------------

    signature = create_signature(
        payload_json,
        webhook.secret
    )

    # -------------------------------------------------
    # VERIFY GENERATED SIGNATURE
    # -------------------------------------------------

    if not verify_signature(
        payload_json,
        signature,
        webhook.secret
    ):
        delivery.status = "failed"
        delivery.response_code = None

        db.commit()
        db.refresh(delivery)

        return delivery

    # -------------------------------------------------
    # RETRY DELIVERY
    # -------------------------------------------------

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        delivery.attempt_count = attempt

        try:

            response = httpx.post(
                webhook.target_url,
                content=payload_json,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Event": event_type,
                    "X-Webhook-Event-ID": event_id
                },
                timeout=10
            )

            delivery.response_code = (
                response.status_code
            )

            # -----------------------------------------
            # SUCCESS
            # -----------------------------------------

            if 200 <= response.status_code < 300:

                delivery.status = "delivered"

                delivery.delivered_at = (
                    datetime.now(timezone.utc)
                )

                db.commit()
                db.refresh(delivery)

                return delivery

        except Exception:

            delivery.response_code = None

        db.commit()

        # ---------------------------------------------
        # RETRY
        # ---------------------------------------------

        if attempt < MAX_RETRIES:
            time.sleep(attempt)

    # -------------------------------------------------
    # FINAL FAILURE
    # -------------------------------------------------

    delivery.status = "failed"

    db.commit()
    db.refresh(delivery)

    return delivery


@router.post(
    "/",
    response_model=WebhookResponse,
    status_code=status.HTTP_201_CREATED
)
def create_webhook(
    data: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        api_provider_required
    )
):

    api = db.query(API).filter(
        API.id == data.api_id
    ).first()

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )

    organization = db.query(
        Organization
    ).filter(
        Organization.id == api.organization_id,
        Organization.owner_id == current_user.id
    ).first()

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create webhooks for your own APIs"
        )

    webhook = Webhook(
        api_id=data.api_id,
        event_type=data.event_type,
        target_url=data.target_url,
        secret=data.secret,
        is_active=data.is_active
    )

    db.add(webhook)
    db.commit()
    db.refresh(webhook)

    return webhook


@router.get(
    "/api/{api_id}",
    response_model=list[WebhookResponse]
)
def get_api_webhooks(
    api_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    api = db.query(API).filter(
        API.id == api_id
    ).first()

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )

    # ---------------------------------------------
    # PROVIDER ACCESS
    # ---------------------------------------------

    if current_user.role == "api_provider":

        organization = db.query(
            Organization
        ).filter(
            Organization.id == api.organization_id,
            Organization.owner_id == current_user.id
        ).first()

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access webhooks of your own APIs"
            )

    # ---------------------------------------------
    # ADMIN ACCESS
    # ---------------------------------------------

    elif current_user.role != "platform_admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return db.query(Webhook).filter(
        Webhook.api_id == api_id
    ).all()


@router.patch(
    "/{webhook_id}/status",
    response_model=WebhookResponse
)
def update_webhook_status(
    webhook_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        api_provider_required
    )
):

    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id
    ).first()

    if webhook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )

    api = db.query(API).filter(
        API.id == webhook.api_id
    ).first()

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )

    organization = db.query(
        Organization
    ).filter(
        Organization.id == api.organization_id,
        Organization.owner_id == current_user.id
    ).first()

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own webhooks"
        )

    webhook.is_active = is_active

    db.commit()
    db.refresh(webhook)

    return webhook


@router.post(
    "/{webhook_id}/test",
    response_model=WebhookDeliveryResponse
)
def test_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        api_provider_required
    )
):

    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id
    ).first()

    if webhook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )

    api = db.query(API).filter(
        API.id == webhook.api_id
    ).first()

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )

    organization = db.query(
        Organization
    ).filter(
        Organization.id == api.organization_id,
        Organization.owner_id == current_user.id
    ).first()

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only test your own webhooks"
        )

    if not webhook.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook is inactive"
        )

    delivery = deliver_webhook(
        webhook=webhook,
        event_type=webhook.event_type,
        payload={
            "message": "Webhook test event",
            "api_id": webhook.api_id
        },
        db=db
    )

    return delivery


@router.get(
    "/{webhook_id}/deliveries",
    response_model=list[WebhookDeliveryResponse]
)
def get_webhook_deliveries(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id
    ).first()

    if webhook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )

    api = db.query(API).filter(
        API.id == webhook.api_id
    ).first()

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )

    # ---------------------------------------------
    # PROVIDER ACCESS
    # ---------------------------------------------

    if current_user.role == "api_provider":

        organization = db.query(
            Organization
        ).filter(
            Organization.id == api.organization_id,
            Organization.owner_id == current_user.id
        ).first()

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view deliveries of your own webhooks"
            )

    # ---------------------------------------------
    # ADMIN ACCESS
    # ---------------------------------------------

    elif current_user.role != "platform_admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return db.query(
        WebhookDelivery
    ).filter(
        WebhookDelivery.webhook_id == webhook_id
    ).all()


@router.post(
    "/{webhook_id}/retry/{delivery_id}",
    response_model=WebhookDeliveryResponse
)
def retry_webhook_delivery(
    webhook_id: int,
    delivery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        api_provider_required
    )
):

    webhook = db.query(Webhook).filter(
        Webhook.id == webhook_id
    ).first()

    if webhook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )

    api = db.query(API).filter(
        API.id == webhook.api_id
    ).first()

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )

    organization = db.query(
        Organization
    ).filter(
        Organization.id == api.organization_id,
        Organization.owner_id == current_user.id
    ).first()

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only retry your own webhook deliveries"
        )

    delivery = db.query(
        WebhookDelivery
    ).filter(
        WebhookDelivery.id == delivery_id,
        WebhookDelivery.webhook_id == webhook_id
    ).first()

    if delivery is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook delivery not found"
        )

    if delivery.status == "delivered":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook delivery already succeeded"
        )

    # ---------------------------------------------
    # RETRY PAYLOAD
    # ---------------------------------------------

    payload = {
        "retry": True,
        "event_id": delivery.event_id
    }

    delivery.status = "pending"

    db.commit()

    payload_json = json.dumps(
        {
            "event_id": delivery.event_id,
            "event_type": webhook.event_type,
            "data": payload
        },
        separators=(",", ":"),
        default=str
    )

    # ---------------------------------------------
    # CREATE SIGNATURE
    # ---------------------------------------------

    signature = create_signature(
        payload_json,
        webhook.secret
    )

    # ---------------------------------------------
    # VERIFY SIGNATURE
    # ---------------------------------------------

    if not verify_signature(
        payload_json,
        signature,
        webhook.secret
    ):
        delivery.status = "failed"

        db.commit()
        db.refresh(delivery)

        return delivery

    # ---------------------------------------------
    # RETRY DELIVERY
    # ---------------------------------------------

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        delivery.attempt_count += 1

        try:

            response = httpx.post(
                webhook.target_url,
                content=payload_json,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Event": webhook.event_type,
                    "X-Webhook-Event-ID": delivery.event_id
                },
                timeout=10
            )

            delivery.response_code = (
                response.status_code
            )

            if 200 <= response.status_code < 300:

                delivery.status = "delivered"

                delivery.delivered_at = (
                    datetime.now(timezone.utc)
                )

                db.commit()
                db.refresh(delivery)

                return delivery

        except Exception:

            delivery.response_code = None

        db.commit()

        if attempt < MAX_RETRIES:
            time.sleep(attempt)

    # ---------------------------------------------
    # FINAL FAILURE
    # ---------------------------------------------

    delivery.status = "failed"

    db.commit()
    db.refresh(delivery)

    return delivery