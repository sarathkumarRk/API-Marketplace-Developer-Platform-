from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, api_provider_required
from app.models.api import API
from app.models.api_plan import APIPlan
from app.models.organization import Organization
from app.models.user import User
from app.schemas.api_plan import APIPlanCreate, APIPlanResponse


router = APIRouter(
    prefix="/api-plans",
    tags=["API Plans"]
)


@router.post(
    "/",
    response_model=APIPlanResponse,
    status_code=status.HTTP_201_CREATED
)
def create_api_plan(
    data: APIPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(api_provider_required)
):
    api = db.query(API).filter(
        API.id == data.api_id
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
            detail="You can only create plans for your own APIs"
        )

    existing_plan = db.query(APIPlan).filter(
        APIPlan.api_id == data.api_id,
        APIPlan.name == data.name
    ).first()

    if existing_plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API plan already exists"
        )

    plan = APIPlan(
        api_id=data.api_id,
        name=data.name,
        price=data.price,
        requests_per_month=data.requests_per_month,
        requests_per_minute=data.requests_per_minute,
        is_active=data.is_active
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return plan


@router.get(
    "/api/{api_id}",
    response_model=list[APIPlanResponse]
)
def get_api_plans(
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

    if current_user.role == "api_provider":
        organization = db.query(Organization).filter(
            Organization.id == api.organization_id,
            Organization.owner_id == current_user.id
        ).first()

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access plans of your own APIs"
            )

        return db.query(APIPlan).filter(
            APIPlan.api_id == api_id
        ).all()

    if current_user.role == "platform_admin":
        return db.query(APIPlan).filter(
            APIPlan.api_id == api_id
        ).all()

    if api.status != "published":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )

    return db.query(APIPlan).filter(
        APIPlan.api_id == api_id,
        APIPlan.is_active == True
    ).all()


@router.get(
    "/{plan_id}",
    response_model=APIPlanResponse
)
def get_api_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = db.query(APIPlan).filter(
        APIPlan.id == plan_id
    ).first()

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API plan not found"
        )

    api = db.query(API).filter(
        API.id == plan.api_id
    ).first()

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )

    if current_user.role == "api_provider":
        organization = db.query(Organization).filter(
            Organization.id == api.organization_id,
            Organization.owner_id == current_user.id
        ).first()

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access plans of your own APIs"
            )

    elif current_user.role == "developer":
        if api.status != "published" or not plan.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API plan not found"
            )

    elif current_user.role != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return plan


@router.patch(
    "/{plan_id}/status",
    response_model=APIPlanResponse
)
def update_plan_status(
    plan_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(api_provider_required)
):
    plan = db.query(APIPlan).filter(
        APIPlan.id == plan_id
    ).first()

    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API plan not found"
        )

    api = db.query(API).filter(
        API.id == plan.api_id
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
            detail="You can only update plans of your own APIs"
        )

    plan.is_active = is_active

    db.commit()
    db.refresh(plan)

    return plan