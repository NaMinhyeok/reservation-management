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
from app.schemas.reservation import ReservationResponse, ReservationUpdate

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
        raise HTTPException(status_code=400, detail="예약은 시험 3일 전까지만 가능합니다.")

    confirmed_seats = sum(
        r.requested_seats
        for r in exam_schedule.reservations
        if r.status == ReservationStatus.CONFIRMED
    )

    if confirmed_seats + request.requested_seats > exam_schedule.max_seats:
        raise HTTPException(status_code=400, detail="충분한 자리가 없습니다.")

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
        raise HTTPException(status_code=403, detail="관리자만 예약을 확정할 수 있습니다.")

    reservation = db.query(Reservation).get(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다.")

    total_confirmed_seats = db.query(func.sum(Reservation.requested_seats))\
        .filter(
            Reservation.exam_id == reservation.exam_id,
            Reservation.status == ReservationStatus.CONFIRMED
        ).scalar() or 0

    if total_confirmed_seats + reservation.requested_seats > reservation.exam_schedule.max_seats:
        raise HTTPException(
            status_code=400,
            detail=f"예약인원 최대치를 초과했습니다. 현재 확정인원: {total_confirmed_seats}, 요청인원: {reservation.requested_seats}"
        )

    reservation.status = ReservationStatus.CONFIRMED
    db.commit()
    db.refresh(reservation)

    return reservation


@router.patch("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
        reservation_id: int,
        update_data: ReservationUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    reservation = db.query(Reservation).join(ExamSchedule).get(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="예약이 존재하지 않습니다.")

    # 관리자가 아닌 경우만 체크
    if current_user.role != UserRole.ADMIN:
        if reservation.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="다른 사용자의 예약을 변경할 수 없습니다.")
        if reservation.status == ReservationStatus.CONFIRMED:
            raise HTTPException(status_code=400, detail="확정된 예약은 변경할 수 없습니다.")
        if update_data.start_time and update_data.start_time < datetime.now() + timedelta(days=3):
            raise HTTPException(status_code=400, detail="시험 3일 전까지만 예약이 변경 가능합니다.")

    if update_data.start_time or update_data.end_time:
        new_start = update_data.start_time or reservation.exam_schedule.start_time
        new_end = update_data.end_time or reservation.exam_schedule.end_time

        if current_user.role != UserRole.ADMIN:  # 관리자가 아닌 경우만 좌석 체크
            overlapping_seats = db.query(func.sum(Reservation.requested_seats)) \
                                    .join(ExamSchedule) \
                                    .filter(
                ExamSchedule.start_time < new_end,
                ExamSchedule.end_time > new_start,
                Reservation.status == ReservationStatus.CONFIRMED,
                Reservation.id != reservation_id
            ).scalar() or 0

            new_seats = update_data.requested_seats or reservation.requested_seats
            if overlapping_seats + new_seats > reservation.exam_schedule.max_seats:
                raise HTTPException(status_code=400, detail="해당 시간에 충분한 자리가 없습니다.")

        reservation.exam_schedule.start_time = new_start
        reservation.exam_schedule.end_time = new_end

    if update_data.requested_seats:
        reservation.requested_seats = update_data.requested_seats

    db.commit()
    db.refresh(reservation)
    return reservation

@router.delete("/{reservation_id}", status_code=204)
async def delete_reservation(
       reservation_id: int,
       db: Session = Depends(get_db),
       current_user: User = Depends(get_current_user)
):
   reservation = db.query(Reservation).get(reservation_id)
   if not reservation:
       raise HTTPException(status_code=404, detail="예약이 존재하지 않습니다.")

   if current_user.role != UserRole.ADMIN:
       if reservation.user_id != current_user.id:
           raise HTTPException(status_code=403, detail="다른 사용자의 예약을 삭제할 수 없습니다.")
       if reservation.status == ReservationStatus.CONFIRMED:
           raise HTTPException(status_code=400, detail="확정된 예약은 삭제할 수 없습니다.")

   db.delete(reservation)
   db.commit()