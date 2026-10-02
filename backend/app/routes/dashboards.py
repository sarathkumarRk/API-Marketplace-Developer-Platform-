from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.api import API
from app.models.api_endpoint import APIEndpoint
from app.models.api_plan import APIPlan
from app.models.api_request_log import APIRequestLog
from app.models.organization import Organization
from app.models.subscription import Subscription
from app.models.user import User


router = APIRouter(
    prefix="/dashboards",
    tags=["Dashboards"]
)


# ADMIN DASHBOARD
@router.get("/admin")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform Admin only"
        )

    total_users = db.query(User).count()

    total_developers = db.query(User).filter(
        User.role == "developer"
    ).count()

    total_providers = db.query(User).filter(
        User.role == "api_provider"
    ).count()

    total_apis = db.query(API).count()

    total_published_apis = db.query(API).filter(
        API.status == "published"
    ).count()

    active_subscriptions = db.query(Subscription).filter(
        Subscription.status == "active"
    ).count()

    total_requests = db.query(APIRequestLog).count()

    successful_requests = db.query(APIRequestLog).filter(
        APIRequestLog.status_code >= 200,
        APIRequestLog.status_code < 400
    ).count()

    failed_requests = db.query(APIRequestLog).filter(
        APIRequestLog.status_code >= 400
    ).count()

    average_response_time = db.query(
        func.avg(APIRequestLog.response_time_ms)
    ).scalar()

    if average_response_time is None:
        average_response_time = 0

    platform_revenue = db.query(
        func.coalesce(func.sum(APIPlan.price), 0)
    ).join(
        Subscription,
        Subscription.plan_id == APIPlan.id
    ).filter(
        Subscription.status == "active"
    ).scalar()

    if platform_revenue is None:
        platform_revenue = 0

    return {
        "total_users": total_users,
        "total_developers": total_developers,
        "total_providers": total_providers,
        "total_apis": total_apis,
        "total_published_apis": total_published_apis,
        "active_subscriptions": active_subscriptions,
        "platform_revenue": float(platform_revenue),
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "average_response_time_ms": round(
            float(average_response_time),
            2
        )
    }


# PROVIDER DASHBOARD
@router.get("/provider")
def get_provider_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "api_provider":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Provider only"
        )

    organizations = db.query(Organization.id).filter(
        Organization.owner_id == current_user.id
    ).all()

    organization_ids = [
        organization[0]
        for organization in organizations
    ]

    if not organization_ids:
        return {
            "total_apis": 0,
            "published_apis": 0,
            "active_developers": 0,
            "total_requests": 0,
            "api_revenue": 0,
            "top_endpoints": [],
            "error_rate": 0,
            "average_response_time_ms": 0
        }

    api_ids = db.query(API.id).filter(
        API.organization_id.in_(organization_ids)
    ).all()

    api_id_list = [
        api_id[0]
        for api_id in api_ids
    ]

    if not api_id_list:
        return {
            "total_apis": 0,
            "published_apis": 0,
            "active_developers": 0,
            "total_requests": 0,
            "api_revenue": 0,
            "top_endpoints": [],
            "error_rate": 0,
            "average_response_time_ms": 0
        }

    total_apis = len(api_id_list)

    published_apis = db.query(API).filter(
        API.id.in_(api_id_list),
        API.status == "published"
    ).count()

    active_developers = db.query(
        func.count(
            func.distinct(Subscription.developer_id)
        )
    ).filter(
        Subscription.api_id.in_(api_id_list),
        Subscription.status == "active"
    ).scalar()

    if active_developers is None:
        active_developers = 0

    total_requests = db.query(APIRequestLog).filter(
        APIRequestLog.api_id.in_(api_id_list)
    ).count()

    failed_requests = db.query(APIRequestLog).filter(
        APIRequestLog.api_id.in_(api_id_list),
        APIRequestLog.status_code >= 400
    ).count()

    average_response_time = db.query(
        func.avg(APIRequestLog.response_time_ms)
    ).filter(
        APIRequestLog.api_id.in_(api_id_list)
    ).scalar()

    if average_response_time is None:
        average_response_time = 0

    if total_requests == 0:
        error_rate = 0
    else:
        error_rate = (
            failed_requests / total_requests
        ) * 100

    # Find most frequently used endpoints
    top_endpoint_rows = db.query(
        APIRequestLog.endpoint_id,
        func.count(APIRequestLog.id).label("request_count")
    ).filter(
        APIRequestLog.api_id.in_(api_id_list)
    ).group_by(
        APIRequestLog.endpoint_id
    ).order_by(
        func.count(APIRequestLog.id).desc()
    ).limit(5).all()

    top_endpoints = []

    for endpoint_id, request_count in top_endpoint_rows:
        endpoint = db.query(APIEndpoint).filter(
            APIEndpoint.id == endpoint_id
        ).first()

        if endpoint:
            top_endpoints.append({
                "endpoint_id": endpoint.id,
                "method": endpoint.method,
                "path": endpoint.path,
                "request_count": request_count
            })

    api_revenue = db.query(
        func.coalesce(func.sum(APIPlan.price), 0)
    ).join(
        Subscription,
        Subscription.plan_id == APIPlan.id
    ).filter(
        Subscription.api_id.in_(api_id_list),
        Subscription.status == "active"
    ).scalar()

    if api_revenue is None:
        api_revenue = 0

    return {
        "total_apis": total_apis,
        "published_apis": published_apis,
        "active_developers": active_developers,
        "total_requests": total_requests,
        "api_revenue": float(api_revenue),
        "top_endpoints": top_endpoints,
        "error_rate": round(
            error_rate,
            2
        ),
        "average_response_time_ms": round(
            float(average_response_time),
            2
        )
    }


# DEVELOPER DASHBOARD
@router.get("/developer")
def get_developer_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Developer only"
        )

    active_subscriptions = db.query(Subscription).filter(
        Subscription.developer_id == current_user.id,
        Subscription.status == "active"
    ).count()

    total_subscriptions = db.query(Subscription).filter(
        Subscription.developer_id == current_user.id
    ).count()

    active_api_ids = db.query(
        Subscription.api_id
    ).filter(
        Subscription.developer_id == current_user.id,
        Subscription.status == "active"
    ).all()

    active_api_id_list = [
        api_id[0]
        for api_id in active_api_ids
    ]

    now = datetime.now(timezone.utc)

    start_of_day = datetime(
        now.year,
        now.month,
        now.day,
        tzinfo=timezone.utc
    )

    start_of_month = datetime(
        now.year,
        now.month,
        1,
        tzinfo=timezone.utc
    )

    requests_today = db.query(APIRequestLog).filter(
        APIRequestLog.developer_id == current_user.id,
        APIRequestLog.request_timestamp >= start_of_day
    ).count()

    monthly_requests = db.query(APIRequestLog).filter(
        APIRequestLog.developer_id == current_user.id,
        APIRequestLog.request_timestamp >= start_of_month
    ).count()

    total_requests = db.query(APIRequestLog).filter(
        APIRequestLog.developer_id == current_user.id
    ).count()

    successful_requests = db.query(APIRequestLog).filter(
        APIRequestLog.developer_id == current_user.id,
        APIRequestLog.status_code >= 200,
        APIRequestLog.status_code < 400
    ).count()

    failed_requests = db.query(APIRequestLog).filter(
        APIRequestLog.developer_id == current_user.id,
        APIRequestLog.status_code >= 400
    ).count()

    average_response_time = db.query(
        func.avg(APIRequestLog.response_time_ms)
    ).filter(
        APIRequestLog.developer_id == current_user.id
    ).scalar()

    if average_response_time is None:
        average_response_time = 0

    rate_limits = []

    if active_api_id_list:
        plans = db.query(APIPlan).filter(
            APIPlan.api_id.in_(active_api_id_list),
            APIPlan.is_active == True
        ).all()

        for plan in plans:
            rate_limits.append({
                "api_id": plan.api_id,
                "plan_name": plan.name,
                "requests_per_minute": plan.requests_per_minute,
                "requests_per_month": plan.requests_per_month
            })

    return {
        "total_subscriptions": total_subscriptions,
        "active_subscriptions": active_subscriptions,
        "active_apis": len(active_api_id_list),
        "api_requests_today": requests_today,
        "monthly_usage": monthly_requests,
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "rate_limits": rate_limits,
        "average_response_time_ms": round(
            float(average_response_time),
            2
        )
    }