# repository.py
from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager

from app.models import ExamSchedule, Reservation
from app.models.enums import ReservationStatus


def get_confirmed_seats_count(schedule: ExamSchedule) -> int:
    return sum(
        r.requested_seats
        for r in schedule.reservations
        if r.status == ReservationStatus.CONFIRMED
    )


class ExamScheduleRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_available_schedules(self, min_date: datetime) -> Sequence[ExamSchedule]:
        stmt = (
            select(ExamSchedule)
            .options(contains_eager(ExamSchedule.reservations))
            .join(ExamSchedule.reservations, isouter=True)
            .filter(
                ExamSchedule.start_time >= min_date,
                Reservation.status == ReservationStatus.CONFIRMED
            )
        )

        return self.db.execute(stmt).unique().scalars().all()
