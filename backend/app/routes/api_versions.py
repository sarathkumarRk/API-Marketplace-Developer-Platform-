from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, api_provider_required
from app.models.api import API
from app.models.api_version import APIVersion
from app.models.organization import Organization
from app.models.user import User
from app.models.webhook import Webhook
from app.schemas.api_version import APIVersionCreate, APIVersionResponse

from app.routes.webhooks import deliver_webhook


router = APIRouter(
    prefix="/api-versions",
    tags=["API Versions"]
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
    response_model=APIVersionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_api_version(
    data: APIVersionCreate,
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
            detail="You can only create versions for your own APIs"
        )

    existing_version = db.query(APIVersion).filter(
        APIVersion.api_id == data.api_id,
        APIVersion.version == data.version
    ).first()

    if existing_version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API version already exists"
        )

    api_version = APIVersion(
        api_id=data.api_id,
        version=data.version,
        base_url=data.base_url,
        status=data.status
    )

    db.add(api_version)
    db.commit()
    db.refresh(api_version)

    return api_version


@router.get(
    "/api/{api_id}",
    response_model=list[APIVersionResponse]
)
def get_api_versions(
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
                detail="You can only access versions of your own APIs"
            )

    elif current_user.role == "developer":
        if api.status != "published":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API not found"
            )

    elif current_user.role != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return db.query(APIVersion).filter(
        APIVersion.api_id == api_id
    ).all()


@router.get(
    "/{version_id}",
    response_model=APIVersionResponse
)
def get_api_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    api_version = db.query(APIVersion).filter(
        APIVersion.id == version_id
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
                detail="You can only access versions of your own APIs"
            )

    elif current_user.role == "developer":
        if api.status != "published":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API version not found"
            )

    elif current_user.role != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return api_version


@router.patch(
    "/{version_id}/status",
    response_model=APIVersionResponse
)
def update_version_status(
    version_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(api_provider_required)
):
    api_version = db.query(APIVersion).filter(
        APIVersion.id == version_id
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
            detail="You can only update versions of your own APIs"
        )

    allowed_statuses = [
        "active",
        "deprecated",
        "retired"
    ]

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid version status"
        )

    old_status = api_version.status

    api_version.status = new_status

    db.commit()
    db.refresh(api_version)

    # Trigger webhook when API version becomes deprecated

    if old_status != "deprecated" and new_status == "deprecated":
        trigger_webhook_event(
            db=db,
            api_id=api.id,
            event_type="api.version.deprecated",
            payload={
                "api_id": api.id,
                "api_version_id": api_version.id,
                "version": api_version.version,
                "status": api_version.status
            }
        )

    return api_version