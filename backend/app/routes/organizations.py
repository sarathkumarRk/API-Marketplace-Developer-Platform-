from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import platform_admin_required
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse
)


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


# CREATE ORGANIZATION
@router.post(
    "/",
    response_model=OrganizationResponse
)
def create_organization(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(platform_admin_required)
):
    owner = db.query(User).filter(
        User.id == data.owner_id,
        User.role == "api_provider"
    ).first()

    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API provider not found"
        )

    organization = Organization(
        name=data.name,
        owner_id=data.owner_id
    )

    db.add(organization)
    db.commit()
    db.refresh(organization)

    return organization


# GET ALL ORGANIZATIONS
@router.get(
    "/",
    response_model=list[OrganizationResponse]
)
def get_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(platform_admin_required)
):
    organizations = db.query(Organization).all()

    return organizations