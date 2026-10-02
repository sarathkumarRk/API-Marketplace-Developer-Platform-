from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.api import API
from app.models.api_request_log import APIRequestLog
from app.models.organization import Organization
from app.models.usage_summary import UsageSummary
from app.models.user import User
from app.schemas.usage import UsageSummaryResponse


router = APIRouter(
    prefix="/usage",
    tags=["Usage"]
)


@router.get(
    "/my",
    response_model=list[UsageSummaryResponse]
)
def get_my_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(UsageSummary).filter(
        UsageSummary.developer_id == current_user.id
    ).all()


@router.get(
    "/api/{api_id}",
    response_model=list[UsageSummaryResponse]
)
def get_api_usage(
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

    if current_user.role == "developer":
        return db.query(UsageSummary).filter(
            UsageSummary.api_id == api_id,
            UsageSummary.developer_id == current_user.id
        ).all()

    if current_user.role == "api_provider":
        organization = db.query(Organization).filter(
            Organization.id == api.organization_id,
            Organization.owner_id == current_user.id
        ).first()

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view usage for your own APIs"
            )

        return db.query(UsageSummary).filter(
            UsageSummary.api_id == api_id
        ).all()

    if current_user.role == "platform_admin":
        return db.query(UsageSummary).filter(
            UsageSummary.api_id == api_id
        ).all()

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


@router.get(
    "/analytics"
)
def get_usage_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(APIRequestLog)

    if current_user.role == "developer":

        query = query.filter(
            APIRequestLog.developer_id == current_user.id
        )

    elif current_user.role == "api_provider":

        organizations = db.query(
            Organization.id
        ).filter(
            Organization.owner_id == current_user.id
        ).all()

        organization_ids = [
            organization[0]
            for organization in organizations
        ]

        if not organization_ids:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time_ms": 0,
                "error_rate": 0
            }

        api_ids = db.query(
            API.id
        ).filter(
            API.organization_id.in_(organization_ids)
        ).all()

        api_id_list = [
            api[0]
            for api in api_ids
        ]

        if not api_id_list:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time_ms": 0,
                "error_rate": 0
            }

        query = query.filter(
            APIRequestLog.api_id.in_(api_id_list)
        )

    elif current_user.role == "platform_admin":
        pass

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    total_requests = query.count()

    successful_requests = query.filter(
        APIRequestLog.status_code >= 200,
        APIRequestLog.status_code < 400
    ).count()

    failed_requests = query.filter(
        APIRequestLog.status_code >= 400
    ).count()

    average_response_time = query.with_entities(
        func.avg(APIRequestLog.response_time_ms)
    ).scalar()

    if average_response_time is None:
        average_response_time = 0

    if total_requests == 0:
        error_rate = 0
    else:
        error_rate = (
            failed_requests / total_requests
        ) * 100

    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "average_response_time_ms": round(
            float(average_response_time),
            2
        ),
        "error_rate": round(
            error_rate,
            2
        )
    }
