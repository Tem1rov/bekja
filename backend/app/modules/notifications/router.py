"""Notifications router."""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from uuid import UUID

from app.auth.permissions import require_permission, Permission
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import NotificationResponse, NotificationListResponse
from .service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    is_read: bool | None = Query(None, alias="is_read"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List notifications for current user."""
    service = NotificationService(db)
    notifications = await service.list_notifications(
        user_id=user.id,
        is_read=is_read,
        limit=limit,
        offset=offset
    )
    unread_count = await service.get_unread_count(user.id)
    
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=len(notifications),
        unread_count=unread_count
    )


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get count of unread notifications."""
    service = NotificationService(db)
    count = await service.get_unread_count(user.id)
    return {"unread_count": count}


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Mark a notification as read."""
    service = NotificationService(db)
    try:
        notification = await service.mark_as_read(notification_id)
        # Check if notification belongs to user
        if notification.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Notification does not belong to current user"
            )
        return NotificationResponse.model_validate(notification)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
