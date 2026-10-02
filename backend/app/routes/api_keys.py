import hashlib
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import developer_required, get_current_user
from app.models.api_key import APIKey
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.api_key import APIKeyCreate, APIKeyResponse
from app.services.email_service import send_api_key_generated_email


router = APIRouter(
    prefix="/api-keys",
    tags=["API Keys"]
)


@router.post(
    "/",
    response_model=APIKeyResponse,
    status_code=status.HTTP_201_CREATED
)
def generate_api_key(
    data: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    if data.developer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only generate keys for yourself"
        )

    subscription = db.query(Subscription).filter(
        Subscription.id == data.subscription_id,
        Subscription.developer_id == current_user.id
    ).first()

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    if subscription.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active subscription required"
        )

    raw_key = secrets.token_urlsafe(32)

    key_prefix = raw_key[:8]

    key_hash = hashlib.sha256(
        raw_key.encode()
    ).hexdigest()

    api_key = APIKey(
        developer_id=current_user.id,
        subscription_id=data.subscription_id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        expires_at=data.expires_at
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    send_api_key_generated_email(
        current_user.email
    )

    response = APIKeyResponse.model_validate(api_key)

    response.full_key = raw_key

    return response


@router.get(
    "/my",
    response_model=list[APIKeyResponse]
)
def get_my_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    return db.query(APIKey).filter(
        APIKey.developer_id == current_user.id
    ).all()


@router.get(
    "/{api_key_id}",
    response_model=APIKeyResponse
)
def get_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id
    ).first()

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    if current_user.role == "developer":

        if api_key.developer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own API keys"
            )

    elif current_user.role != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return api_key


@router.patch(
    "/{api_key_id}/revoke",
    response_model=APIKeyResponse
)
def revoke_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.developer_id == current_user.id
    ).first()

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    if not api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key is already revoked"
        )

    api_key.is_active = False

    db.commit()
    db.refresh(api_key)

    return api_key


@router.post(
    "/{api_key_id}/regenerate",
    response_model=APIKeyResponse
)
def regenerate_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(developer_required)
):
    old_api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.developer_id == current_user.id
    ).first()

    if old_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    if not old_api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot regenerate a revoked API key"
        )

    subscription = db.query(Subscription).filter(
        Subscription.id == old_api_key.subscription_id,
        Subscription.developer_id == current_user.id
    ).first()

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    if subscription.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active subscription required"
        )

    old_api_key.is_active = False

    raw_key = secrets.token_urlsafe(32)

    key_prefix = raw_key[:8]

    key_hash = hashlib.sha256(
        raw_key.encode()
    ).hexdigest()

    new_api_key = APIKey(
        developer_id=current_user.id,
        subscription_id=old_api_key.subscription_id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        expires_at=old_api_key.expires_at
    )

    db.add(new_api_key)
    db.commit()
    db.refresh(new_api_key)

    send_api_key_generated_email(
        current_user.email
    )

    response = APIKeyResponse.model_validate(new_api_key)

    response.full_key = raw_key

    return response


