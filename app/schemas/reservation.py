from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from app.models.enums import ReservationStatus


class ReservationResponse(BaseModel):
    id: int
    user_id: int
    exam_id: int
    status: ReservationStatus
    requested_seats: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReservationUpdate(BaseModel):
    requested_seats: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @validator('requested_seats')
    def validate_seats(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Requested seats must be positive")
        return v

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if v and 'start_time' in values and values['start_time']:
            if v <= values['start_time']:
                raise ValueError("End time must be after start time")
        return v