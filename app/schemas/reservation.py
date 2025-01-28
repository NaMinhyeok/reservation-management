from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReservationResponse(BaseModel):
    id: int
    user_id: int
    exam_id: int
    status: str
    requested_seats: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReservationUpdate(BaseModel):
    requested_seats: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @classmethod
    def validate_seats(cls, v):
        if v is not None and v <= 0:
            raise ValueError("요청 좌석은 0보다 커야합니다.")
        return v

    @classmethod
    def validate_end_time(cls, v, info):
        if v and info.data.get('start_time'):
            if v <= info.data['start_time']:
                raise ValueError("종료 시각은 시작 시각보다 커야합니다.")
        return v


class CreateReservationRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    requested_seats: int
