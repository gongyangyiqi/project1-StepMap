from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import AppError, ErrorCode
from app.db.session import get_db
from app.models.footprint import Footprint
from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip import TripCreate, TripDetail, TripPublic

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("", response_model=TripPublic, status_code=status.HTTP_201_CREATED)
def create_trip(
    payload: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TripPublic:
    trip = Trip(
        user_id=current_user.id,
        title=payload.title,
        start_date=payload.start_date,
        end_date=payload.end_date,
        cover_image_url=payload.cover_image_url,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return TripPublic.model_validate(trip, from_attributes=True)


@router.get("", response_model=list[TripDetail])
def list_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TripDetail]:
    stmt = (
        select(
            Trip,
            func.count(Footprint.id).label("footprint_count"),
        )
        .outerjoin(Footprint, Trip.id == Footprint.trip_id)
        .where(Trip.user_id == current_user.id)
        .group_by(Trip.id)
        .order_by(Trip.created_at.desc())
    )
    results = db.execute(stmt).all()

    trips: list[TripDetail] = []
    for trip, count in results:
        detail = TripDetail.model_validate(trip, from_attributes=True)
        detail.footprint_count = count or 0
        trips.append(detail)
    return trips


@router.get("/{trip_id}", response_model=TripDetail)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TripDetail:
    trip = db.get(Trip, trip_id)
    if trip is None or trip.user_id != current_user.id:
        raise AppError(
            message="Trip not found.",
            code=ErrorCode.RESOURCE_ERROR,
            status_code=404,
        )

    count = db.scalar(
        select(func.count(Footprint.id)).where(Footprint.trip_id == trip_id)
    )
    detail = TripDetail.model_validate(trip, from_attributes=True)
    detail.footprint_count = count or 0
    return detail


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    trip = db.get(Trip, trip_id)
    if trip is None or trip.user_id != current_user.id:
        raise AppError(
            message="Trip not found.",
            code=ErrorCode.RESOURCE_ERROR,
            status_code=404,
        )
    db.delete(trip)
    db.commit()
