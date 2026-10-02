from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import platform_admin_required
from app.services.advanced_sql import ADVANCED_SQL_QUERIES


router = APIRouter(
    prefix="/advanced-sql",
    tags=["Advanced SQL"]
)


def execute_query(
    query_name: str,
    db: Session
):
    query = ADVANCED_SQL_QUERIES.get(query_name)

    if query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SQL query not found"
        )

    result = db.execute(query)

    return [dict(row) for row in result.mappings().all()]


@router.get("/most-used-apis")
def most_used_apis(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query("most_used_apis", db)


@router.get("/most-used-endpoints")
def most_used_endpoints(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query("most_used_endpoints", db)


@router.get("/top-developers")
def top_developers(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query("top_developers_by_usage", db)


@router.get("/api-revenue-by-month")
def api_revenue_by_month(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query("api_revenue_by_month", db)


@router.get("/provider-wise-revenue")
def provider_wise_revenue(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query("provider_wise_revenue", db)


@router.get("/average-api-response-time")
def average_api_response_time(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query("average_api_response_time", db)


@router.get("/highest-error-rate")
def highest_error_rate(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query("apis_with_highest_error_rate", db)


@router.get("/developers-over-80-percent-quota")
def developers_over_80_percent_quota(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query(
        "developers_exceeding_80_percent_quota",
        db
    )


@router.get("/popular-subscription-plans")
def popular_subscription_plans(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query(
        "most_popular_subscription_plans",
        db
    )


@router.get("/cancelled-subscriptions-by-month")
def cancelled_subscriptions_by_month(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query(
        "cancelled_subscriptions_per_month",
        db
    )


@router.get("/api-usage-by-version")
def api_usage_by_version(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query(
        "api_usage_by_version",
        db
    )


@router.get("/deprecated-versions-with-requests")
def deprecated_versions_with_requests(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query(
        "deprecated_versions_receiving_requests",
        db
    )


@router.get("/failed-webhook-deliveries")
def failed_webhook_deliveries(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query(
        "failed_webhook_deliveries",
        db
    )


@router.get("/daily-api-request-statistics")
def daily_api_request_statistics(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query(
        "daily_api_request_statistics",
        db
    )


@router.get("/monthly-platform-revenue")
def monthly_platform_revenue(
    db: Session = Depends(get_db),
    current_user=Depends(platform_admin_required)
):
    return execute_query(
        "monthly_platform_revenue",
        db
    )