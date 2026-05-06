from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TripCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date
    cover_image_url: str | None = None

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, end_date: date, info) -> date:
        start = info.data.get("start_date")
        if start and end_date < start:
            raise ValueError("End date cannot be earlier than start date.")
        return end_date


class TripPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    start_date: date
    end_date: date
    cover_image_url: str | None = None
    created_at: datetime


class TripDetail(TripPublic):
    footprint_count: int = 0
