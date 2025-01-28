from datetime import datetime

from pydantic import BaseModel


class AvailableExamScheduleResponse(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    max_seats: int
    available_seats: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
