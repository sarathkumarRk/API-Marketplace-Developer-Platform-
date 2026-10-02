from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import (
    get_current_user,
    api_provider_required,
    platform_admin_required
)
from app.models.api import API
from app.models.organization import Organization
from app.models.user import User
from app.schemas.api import APICreate, APIResponse
from app.services.email_service import (
    send_api_approved_email,
    send_api_rejected_email
)


router = APIRouter(
    prefix="/apis",
    tags=["APIs"]
)


@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED
)
def create_api(
    data: APICreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(api_provider_required)
):
    organization = db.query(Organization).filter(
        Organization.id == data.organization_id,
        Organization.owner_id == current_user.id
    ).first()

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create APIs for your own organization"
        )

    existing_api = db.query(API).filter(
        API.slug == data.slug
    ).first()

    if existing_api:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API slug already exists"
        )

    api = API(
        organization_id=data.organization_id,
        name=data.name,
        slug=data.slug,
        description=data.description,
        category=data.category,
        status="draft"
    )

    db.add(api)
    db.commit()
    db.refresh(api)

    return api


@router.get(
    "/",
    response_model=list[APIResponse]
)
def get_apis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "platform_admin":
        return db.query(API).all()

    if current_user.role == "api_provider":
        organizations = db.query(Organization.id).filter(
            Organization.owner_id == current_user.id
        ).all()

        organization_ids = [
            organization[0]
            for organization in organizations
        ]

        if not organization_ids:
            return []

        return db.query(API).filter(
            API.organization_id.in_(organization_ids)
        ).all()

    if current_user.role == "developer":
        return db.query(API).filter(
            API.status == "published"
        ).all()

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


@router.get(
    "/{api_id}",
    response_model=APIResponse
)
def get_api(
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

    if current_user.role == "platform_admin":
        return api

    if current_user.role == "api_provider":
        organization = db.query(Organization).filter(
            Organization.id == api.organization_id,
            Organization.owner_id == current_user.id
        ).first()

        if organization is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own APIs"
            )

        return api

    if current_user.role == "developer":
        if api.status != "published":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API not found"
            )

        return api

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied"
    )


@router.post(
    "/{api_id}/submit",
    response_model=APIResponse
)
def submit_api(
    api_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(api_provider_required)
):
    api = db.query(API).filter(
        API.id == api_id
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
            detail="You can only submit your own APIs"
        )

    if api.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only draft APIs can be submitted"
        )

    api.status = "submitted"

    db.commit()
    db.refresh(api)

    return api


@router.post(
    "/{api_id}/review",
    response_model=APIResponse
)
def review_api(
    api_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(platform_admin_required)
):
    api = db.query(API).filter(
        API.id == api_id
    ).first()

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )

    if api.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only submitted APIs can be moved to admin review"
        )

    api.status = "admin_review"

    db.commit()
    db.refresh(api)

    return api


@router.post(
    "/{api_id}/approve",
    response_model=APIResponse
)
def approve_api(
    api_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(platform_admin_required)
):
    api = db.query(API).filter(
        API.id == api_id
    ).first()

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )

    if api.status != "admin_review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only APIs under admin review can be approved"
        )

    api.status = "approved"

    db.commit()
    db.refresh(api)

    organization = db.query(Organization).filter(
        Organization.id == api.organization_id
    ).first()

    if organization:
        provider = db.query(User).filter(
            User.id == organization.owner_id
        ).first()

        if provider:
            send_api_approved_email(provider.email)

    return api


@router.post(
    "/{api_id}/reject",
    response_model=APIResponse
)
def reject_api(
    api_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(platform_admin_required)
):
    api = db.query(API).filter(
        API.id == api_id
    ).first()

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )

    if api.status != "admin_review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only APIs under admin review can be rejected"
        )

    api.status = "rejected"

    db.commit()
    db.refresh(api)

    organization = db.query(Organization).filter(
        Organization.id == api.organization_id
    ).first()

    if organization:
        provider = db.query(User).filter(
            User.id == organization.owner_id
        ).first()

        if provider:
            send_api_rejected_email(provider.email)

    return api


@router.post(
    "/{api_id}/return-to-draft",
    response_model=APIResponse
)
def return_api_to_draft(
    api_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(api_provider_required)
):
    api = db.query(API).filter(
        API.id == api_id
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
            detail="You can only update your own APIs"
        )

    if api.status != "rejected":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only rejected APIs can be returned to draft"
        )

    api.status = "draft"

    db.commit()
    db.refresh(api)

    return api


@router.post(
    "/{api_id}/publish",
    response_model=APIResponse
)
def publish_api(
    api_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(api_provider_required)
):
    api = db.query(API).filter(
        API.id == api_id
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
            detail="You can only publish your own APIs"
        )

    if api.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approved APIs can be published"
        )

    api.status = "published"

    db.commit()
    db.refresh(api)

    return api


@router.post(
    "/{api_id}/suspend",
    response_model=APIResponse
)
def suspend_api(
    api_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(platform_admin_required)
):
    api = db.query(API).filter(
        API.id == api_id
    ).first()

    if api is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API not found"
        )

    if api.status != "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only published APIs can be suspended"
        )

    api.status = "suspended"

    db.commit()
    db.refresh(api)

    return api