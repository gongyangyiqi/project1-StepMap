from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FootprintCreate(BaseModel):
    trip_id: int
    image_url: str = Field(min_length=1)
    note: str = Field(min_length=1, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    location_name: str | None = Field(default=None, max_length=200)
    recorded_at: datetime


class FootprintPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    image_url: str
    note: str
    latitude: float
    longitude: float
    location_name: str | None = None
    recorded_at: datetime
    created_at: datetime
