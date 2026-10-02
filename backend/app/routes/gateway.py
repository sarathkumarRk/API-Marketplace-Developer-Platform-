import hashlib

from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response

from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import developer_required

from app.models.api import API
from app.models.api_endpoint import APIEndpoint
from app.models.api_key import APIKey
from app.models.api_plan import APIPlan
from app.models.api_request_log import APIRequestLog
from app.models.api_version import APIVersion
from app.models.subscription import Subscription
from app.models.usage_summary import UsageSummary
from app.models.user import User
from app.models.webhook import Webhook

from app.services.email_service import (
    send_rate_limit_exceeded_email
)

from app.services.gateway_service import forward_request

from app.services.redis_service import check_rate_limit

from app.routes.webhooks import deliver_webhook


router = APIRouter(
    prefix="/api-gateway",
    tags=["API Gateway"]
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


def update_usage_summary(
    db: Session,
    developer_id: int,
    api_id: int,
    status_code: int
):
    now = datetime.now(timezone.utc)

    period_start = datetime(
        now.year,
        now.month,
        now.day,
        tzinfo=timezone.utc
    )

    period_end = period_start + timedelta(days=1)

    usage_summary = db.query(UsageSummary).filter(
        UsageSummary.developer_id == developer_id,
        UsageSummary.api_id == api_id,
        UsageSummary.period_start == period_start,
        UsageSummary.period_end == period_end
    ).first()

    if usage_summary is None:
        usage_summary = UsageSummary(
            developer_id=developer_id,
            api_id=api_id,
            period_start=period_start,
            period_end=period_end,
            total_requests=0,
            successful_requests=0,
            failed_requests=0
        )

        db.add(usage_summary)

    usage_summary.total_requests += 1

    if 200 <= status_code < 400:
        usage_summary.successful_requests += 1
    else:
        usage_summary.failed_requests += 1


async def process_gateway_request(
    api_slug: str,
    path: str,
    request: Request,
    db: Session,
    current_user: User
):
    api_key_value = request.headers.get("X-API-Key")

    if not api_key_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )

    api = db.query(API).filter(
        API.slug == api_slug,
        API.status == "published"
    ).first()

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )

    api_key_hash = hashlib.sha256(
        api_key_value.encode()
    ).hexdigest()

    api_key = db.query(APIKey).filter(
        APIKey.key_hash == api_key_hash,
        APIKey.developer_id == current_user.id,
        APIKey.is_active == True
    ).first()

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key"
        )

    if api_key.expires_at is not None:
        key_expires_at = api_key.expires_at

        if key_expires_at.tzinfo is None:
            key_expires_at = key_expires_at.replace(
                tzinfo=timezone.utc
            )

        if key_expires_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key expired"
            )

    subscription = db.query(Subscription).filter(
        Subscription.id == api_key.subscription_id,
        Subscription.developer_id == current_user.id,
        Subscription.api_id == api.id,
        Subscription.status == "active"
    ).first()

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required"
        )

    if subscription.expires_at is not None:
        subscription_expires_at = subscription.expires_at

        if subscription_expires_at.tzinfo is None:
            subscription_expires_at = (
                subscription_expires_at.replace(
                    tzinfo=timezone.utc
                )
            )

        if subscription_expires_at <= datetime.now(
            timezone.utc
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Subscription expired"
            )

    version = request.headers.get("X-API-Version")

    if not version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API version required"
        )

    api_version = db.query(APIVersion).filter(
        APIVersion.api_id == api.id,
        APIVersion.version == version
    ).first()

    if api_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API version not found"
        )

    if api_version.status == "retired":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API version is retired"
        )

    if api_version.status not in [
        "active",
        "deprecated"
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API version is not available"
        )

    endpoint = db.query(APIEndpoint).filter(
        APIEndpoint.api_version_id == api_version.id,
        APIEndpoint.method == request.method,
        APIEndpoint.path == f"/{path}"
    ).first()

    if endpoint is None:
        endpoint = db.query(APIEndpoint).filter(
            APIEndpoint.api_version_id == api_version.id,
            APIEndpoint.method == request.method,
            APIEndpoint.path == path
        ).first()

    if endpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API endpoint not found"
        )

    plan = db.query(APIPlan).filter(
        APIPlan.id == subscription.plan_id,
        APIPlan.api_id == api.id,
        APIPlan.is_active == True
    ).first()

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )

    rate_limit_key = (
        f"rate_limit:{current_user.id}:{api.id}"
    )

    rate_limit_result = check_rate_limit(
        rate_limit_key,
        plan.requests_per_minute
    )

    allowed = rate_limit_result["allowed"]
    remaining = rate_limit_result["remaining"]
    reset = rate_limit_result["reset"]

    if not allowed:
        api_key.last_used_at = datetime.now(
            timezone.utc
        )

        db.commit()

        send_rate_limit_exceeded_email(
            current_user.email
        )

        trigger_webhook_event(
            db=db,
            api_id=api.id,
            event_type="api.request.limit_reached",
            payload={
                "api_id": api.id,
                "api_slug": api.slug,
                "developer_id": current_user.id,
                "api_key_id": api_key.id,
                "subscription_id": subscription.id,
                "plan_id": plan.id,
                "requests_per_minute": plan.requests_per_minute,
                "remaining": remaining,
                "reset": reset
            }
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(
                    plan.requests_per_minute
                ),
                "X-RateLimit-Remaining": str(
                    remaining
                ),
                "X-RateLimit-Reset": str(
                    reset
                )
            }
        )

    request_body = None

    if request.method in [
        "POST",
        "PUT",
        "PATCH"
    ]:
        try:
            request_body = await request.json()
        except Exception:
            request_body = None

    request_headers = dict(request.headers)

    request_headers.pop(
        "host",
        None
    )

    request_headers.pop(
        "content-length",
        None
    )

    request_headers.pop(
        "x-api-key",
        None
    )

    request_headers.pop(
        "x-api-version",
        None
    )

    result = forward_request(
        base_url=api_version.base_url,
        path=path,
        method=request.method,
        headers=request_headers,
        params=dict(request.query_params),
        body=request_body
    )

    response_time_ms = result[
        "response_time_ms"
    ]

    api_key.last_used_at = datetime.now(
        timezone.utc
    )

    request_log = APIRequestLog(
        api_id=api.id,
        api_version_id=api_version.id,
        developer_id=current_user.id,
        endpoint_id=endpoint.id,
        api_key_id=api_key.id,
        method=request.method,
        status_code=result["status_code"],
        response_time_ms=response_time_ms,
        request_timestamp=datetime.now(
            timezone.utc
        )
    )

    db.add(request_log)

    update_usage_summary(
        db=db,
        developer_id=current_user.id,
        api_id=api.id,
        status_code=result["status_code"]
    )

    db.commit()

    response_headers = {
        "X-RateLimit-Limit": str(
            plan.requests_per_minute
        ),
        "X-RateLimit-Remaining": str(
            remaining
        ),
        "X-RateLimit-Reset": str(
            reset
        )
    }

    if api_version.status == "deprecated":
        response_headers["Warning"] = (
            "API version is deprecated"
        )

    return Response(
        content=result["body"],
        status_code=result["status_code"],
        headers=response_headers,
        media_type=result["headers"].get(
            "content-type",
            "application/json"
        )
    )


@router.get("/{api_slug}/{path:path}")
async def api_gateway_get(
    api_slug: str,
    path: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    return await process_gateway_request(
        api_slug=api_slug,
        path=path,
        request=request,
        db=db,
        current_user=current_user
    )


@router.post("/{api_slug}/{path:path}")
async def api_gateway_post(
    api_slug: str,
    path: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    return await process_gateway_request(
        api_slug=api_slug,
        path=path,
        request=request,
        db=db,
        current_user=current_user
    )


@router.put("/{api_slug}/{path:path}")
async def api_gateway_put(
    api_slug: str,
    path: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    return await process_gateway_request(
        api_slug=api_slug,
        path=path,
        request=request,
        db=db,
        current_user=current_user
    )


@router.patch("/{api_slug}/{path:path}")
async def api_gateway_patch(
    api_slug: str,
    path: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    return await process_gateway_request(
        api_slug=api_slug,
        path=path,
        request=request,
        db=db,
        current_user=current_user
    )


@router.delete("/{api_slug}/{path:path}")
async def api_gateway_delete(
    api_slug: str,
    path: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    return await process_gateway_request(
        api_slug=api_slug,
        path=path,
        request=request,
        db=db,
        current_user=current_user
    )