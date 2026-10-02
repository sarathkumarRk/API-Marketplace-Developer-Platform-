from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, api_provider_required
from app.models.api import API
from app.models.api_endpoint import APIEndpoint
from app.models.api_version import APIVersion
from app.models.organization import Organization
from app.models.user import User
from app.schemas.api_endpoint import (
    APIEndpointCreate,
    APIEndpointResponse
)


router = APIRouter(
    prefix="/api-endpoints",
    tags=["API Endpoints"]
)


@router.post(
    "/",
    response_model=APIEndpointResponse,
    status_code=status.HTTP_201_CREATED
)
def create_api_endpoint(
    data: APIEndpointCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(api_provider_required)
):
    api_version = db.query(APIVersion).filter(
        APIVersion.id == data.api_version_id
    ).first()

    if api_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API version not found"
        )

    api = db.query(API).filter(
        API.id == api_version.api_id
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
            detail="You can only create endpoints for your own APIs"
        )

    existing_endpoint = db.query(APIEndpoint).filter(
        APIEndpoint.api_version_id == data.api_version_id,
        APIEndpoint.method == data.method,
        APIEndpoint.path == data.path
    ).first()

    if existing_endpoint:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Endpoint already exists"
        )

    endpoint = APIEndpoint(
        api_version_id=data.api_version_id,
        method=data.method.upper(),
        path=data.path,
        description=data.description,
        authentication_required=data.authentication_required
    )

    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)

    return endpoint


@router.get(
    "/version/{api_version_id}",
    response_model=list[APIEndpointResponse]
)
def get_version_endpoints(
    api_version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    api_version = db.query(APIVersion).filter(
        APIVersion.id == api_version_id
    ).first()

    if api_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API version not found"
        )

    api = db.query(API).filter(
        API.id == api_version.api_id
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
                detail="You can only access endpoints of your own APIs"
            )

    elif current_user.role == "developer":

        if api.status != "published":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API not found"
            )

        if api_version.status not in [
            "active",
            "deprecated"
        ]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API version is not available"
            )

    elif current_user.role != "platform_admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return db.query(APIEndpoint).filter(
        APIEndpoint.api_version_id == api_version_id
    ).all()


@router.get(
    "/{endpoint_id}",
    response_model=APIEndpointResponse
)
def get_api_endpoint(
    endpoint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    endpoint = db.query(APIEndpoint).filter(
        APIEndpoint.id == endpoint_id
    ).first()

    if endpoint is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API endpoint not found"
        )

    api_version = db.query(APIVersion).filter(
        APIVersion.id == endpoint.api_version_id
    ).first()

    if api_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API version not found"
        )

    api = db.query(API).filter(
        API.id == api_version.api_id
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
                detail="You can only access endpoints of your own APIs"
            )

    elif current_user.role == "developer":

        if api.status != "published":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API endpoint not found"
            )

        if api_version.status not in [
            "active",
            "deprecated"
        ]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API version is not available"
            )

    elif current_user.role != "platform_admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return endpoint