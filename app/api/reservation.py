from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models import Reservation, User, ExamSchedule
from app.models.enums import UserRole, ReservationStatus
from app.schemas.reservation import ReservationResponse

router = APIRouter(prefix="/reservations", tags=["reservations"])


class CreateReservationRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    requested_seats: int


@router.post("/", response_model=ReservationResponse)
def create_reservation(
        request: CreateReservationRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    exam_schedule = (
        db.query(ExamSchedule)
        .filter(
            and_(
                ExamSchedule.start_time == request.start_time,
                ExamSchedule.end_time == request.end_time
            )
        )
        .options(joinedload(ExamSchedule.reservations))
        .first()
    )

    if not exam_schedule:
        exam_schedule = ExamSchedule(
            start_time=request.start_time,
            end_time=request.end_time
        )
        db.add(exam_schedule)
        db.flush()

    if exam_schedule.start_time <= datetime.now() + timedelta(days=3):
        raise HTTPException(status_code=400, detail="Reservations must be made at least 3 days before the exam")

    confirmed_seats = sum(
        r.requested_seats
        for r in exam_schedule.reservations
        if r.status == ReservationStatus.CONFIRMED
    )

    if confirmed_seats + request.requested_seats > exam_schedule.max_seats:
        raise HTTPException(status_code=400, detail="Not enough available seats")

    new_reservation = Reservation(
        user_id=current_user.id,
        exam_id=exam_schedule.id,
        requested_seats=request.requested_seats,
        status=ReservationStatus.PENDING
    )

    exam_schedule.reservations.append(new_reservation)
    db.commit()

    return new_reservation

@router.get("/", response_model=List[ReservationResponse])
def get_reservations(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role == UserRole.ADMIN:
        return db.query(Reservation).all()
    return db.query(Reservation).filter(Reservation.user_id == current_user.id).all()

@router.patch("/{reservation_id}/confirm", response_model=ReservationResponse)
async def confirm_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can confirm reservations")

    reservation = db.query(Reservation).get(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # 확정된(CONFIRMED) 예약만 카운트
    total_confirmed_seats = db.query(func.sum(Reservation.requested_seats))\
        .filter(
            Reservation.exam_id == reservation.exam_id,
            Reservation.status == ReservationStatus.CONFIRMED
        ).scalar() or 0

    if total_confirmed_seats + reservation.requested_seats > reservation.exam_schedule.max_seats:
        raise HTTPException(
            status_code=400,
            detail=f"Exceeds maximum capacity. Current confirmed: {total_confirmed_seats}, Requested: {reservation.requested_seats}"
        )

    reservation.status = ReservationStatus.CONFIRMED
    db.commit()
    db.refresh(reservation)

    return reservation