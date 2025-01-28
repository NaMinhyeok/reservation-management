from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

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

    @field_validator('requested_seats')
    def validate_seats(self, v):
        if v is not None and v <= 0:
            raise ValueError("예약인원은 0보다 커야 합니다.")
        return v

    @field_validator('end_time')
    def validate_end_time(self, v, values):
        if v and 'start_time' in values and values['start_time']:
            if v <= values['start_time']:
                raise ValueError("종료시간은 시작시간보다 뒤에 있어야 합니다.")
        return v


class CreateReservationRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    requested_seats: int
