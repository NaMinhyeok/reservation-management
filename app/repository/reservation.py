from datetime import datetime
from typing import Type, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from app.models import ExamSchedule, Reservation
from app.models.enums import ReservationStatus


class ReservationRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_exam_schedule(self, start_time: datetime, end_time: datetime) -> Optional[Type[ExamSchedule]]:
        return (
            self.db.query(ExamSchedule)
            .filter(
                and_(
                    ExamSchedule.start_time == start_time,
                    ExamSchedule.end_time == end_time
                )
            )
            .options(joinedload(ExamSchedule.reservations))
            .first()
        )

    def get_confirmed_seats_count(self, exam_id: int) -> int:
        return (
                self.db.query(func.sum(Reservation.requested_seats))
                .filter(
                    Reservation.exam_id == exam_id,
                    Reservation.status == ReservationStatus.CONFIRMED
                )
                .scalar() or 0
        )

    def get_reservation_by_id(self, reservation_id: int) -> Reservation:
        return self.db.query(Reservation).get(reservation_id)

    def get_all_reservations(self) -> list[Type[Reservation]]:
        return self.db.query(Reservation).all()

    def get_user_reservations(self, user_id: int) -> list[Type[Reservation]]:
        return (
            self.db.query(Reservation)
            .filter(Reservation.user_id == user_id)
            .all()
        )

    def save(self, obj):
        self.db.add(obj)
        self.db.flush()

    def delete(self, obj):
        self.db.delete(obj)
        self.db.commit()

    def commit(self):
        self.db.commit()

    def refresh(self, obj):
        self.db.refresh(obj)
