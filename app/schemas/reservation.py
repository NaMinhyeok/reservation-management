from datetime import datetime

from pydantic import BaseModel

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
