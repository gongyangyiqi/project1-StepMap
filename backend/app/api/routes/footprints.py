from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import AppError, ErrorCode
from app.db.session import get_db
from app.models.footprint import Footprint
from app.models.trip import Trip
from app.models.user import User
from app.schemas.footprint import FootprintCreate, FootprintPublic

router = APIRouter(prefix="/footprints", tags=["footprints"])


@router.post("", response_model=FootprintPublic, status_code=status.HTTP_201_CREATED)
def create_footprint(
    payload: FootprintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FootprintPublic:
    trip = db.get(Trip, payload.trip_id)
    if trip is None or trip.user_id != current_user.id:
        raise AppError(
            message="Trip not found.",
            code=ErrorCode.RESOURCE_ERROR,
            status_code=404,
        )

    footprint = Footprint(
        trip_id=payload.trip_id,
        image_url=payload.image_url,
        note=payload.note,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_name=payload.location_name,
        recorded_at=payload.recorded_at,
    )
    db.add(footprint)
    db.commit()
    db.refresh(footprint)
    return FootprintPublic.model_validate(footprint, from_attributes=True)


@router.get("/trip/{trip_id}", response_model=list[FootprintPublic])
def list_footprints_by_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FootprintPublic]:
    trip = db.get(Trip, trip_id)
    if trip is None or trip.user_id != current_user.id:
        raise AppError(
            message="Trip not found.",
            code=ErrorCode.RESOURCE_ERROR,
            status_code=404,
        )

    footprints = db.scalars(
        select(Footprint)
        .where(Footprint.trip_id == trip_id)
        .order_by(Footprint.recorded_at.desc())
    ).all()
    return [
        FootprintPublic.model_validate(f, from_attributes=True) for f in footprints
    ]


@router.get("/map", response_model=list[FootprintPublic])
def list_all_footprints_for_map(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[FootprintPublic]:
    footprints = db.scalars(
        select(Footprint)
        .join(Trip, Footprint.trip_id == Trip.id)
        .where(Trip.user_id == current_user.id)
        .order_by(Footprint.recorded_at.desc())
    ).all()
    return [
        FootprintPublic.model_validate(f, from_attributes=True) for f in footprints
    ]
