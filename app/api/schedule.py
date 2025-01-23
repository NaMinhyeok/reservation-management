from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, contains_eager

from app.core.database import get_db
from app.models import ExamSchedule
from app.models.reservation import Reservation
from app.models.enums import ReservationStatus
from app.schemas.schedule import AvailableExamScheduleResponse

router = APIRouter(prefix="/exam-schedules", tags=["exam-schedules"])


@router.get("/available", response_model=List[AvailableExamScheduleResponse])
async def get_available_schedules(db: Session = Depends(get_db)):
    min_available_date = datetime.now() + timedelta(days=3)

    stmt = (
        select(ExamSchedule)
        .options(contains_eager(ExamSchedule.reservations))
        .join(ExamSchedule.reservations, isouter=True)
        .filter(
            ExamSchedule.start_time >= min_available_date,
            Reservation.status == ReservationStatus.CONFIRMED
        )
    )

    schedules = db.execute(stmt).unique().scalars().all()

    return [
        AvailableExamScheduleResponse(
            **schedule.__dict__,
            available_seats=schedule.max_seats - sum(
                r.requested_seats for r in schedule.reservations
                if r.status == ReservationStatus.CONFIRMED
            )
        )
        for schedule in schedules
    ]