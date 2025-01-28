from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import func

from app.models import User, ExamSchedule, Reservation
from app.models.enums import UserRole, ReservationStatus
from app.repository.reservation import ReservationRepository
from app.schemas.reservation import ReservationUpdate, CreateReservationRequest


class ReservationService:
    def __init__(self, repository: ReservationRepository):
        self.repository = repository

    def create_reservation(self, request: CreateReservationRequest, current_user: User) -> Reservation:
        exam_schedule = self.repository.find_exam_schedule(
            request.start_time,
            request.end_time
        )

        if not exam_schedule:
            exam_schedule = ExamSchedule(
                start_time=request.start_time,
                end_time=request.end_time
            )
            self.repository.save(exam_schedule)

        self._validate_reservation_date(exam_schedule.start_time)
        self._validate_available_seats(exam_schedule, request.requested_seats)

        new_reservation = Reservation(
            user_id=current_user.id,
            exam_id=exam_schedule.id,
            requested_seats=request.requested_seats,
            status=ReservationStatus.PENDING
        )

        exam_schedule.reservations.append(new_reservation)
        self.repository.commit()

        return new_reservation

    def confirm_reservation(self, reservation_id: int, current_user: User) -> Reservation:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="관리자만 예약을 확정할 수 있습니다.")

        reservation = self._get_reservation_or_404(reservation_id)

        total_confirmed_seats = self.repository.get_confirmed_seats_count(reservation.exam_id)

        if total_confirmed_seats + reservation.requested_seats > reservation.exam_schedule.max_seats:
            raise HTTPException(
                status_code=400,
                detail=f"예약인원 최대치를 초과했습니다. 현재 확정인원: {total_confirmed_seats}, 요청인원: {reservation.requested_seats}"
            )

        reservation.status = ReservationStatus.CONFIRMED
        self.repository.commit()
        self.repository.refresh(reservation)

        return reservation

    def update_reservation(
            self,
            reservation_id: int,
            update_data: ReservationUpdate,
            current_user: User
    ) -> Reservation:
        reservation = self._get_reservation_or_404(reservation_id)

        if not self._can_modify_reservation(reservation, current_user):
            raise HTTPException(status_code=403, detail="다른 사용자의 예약을 변경할 수 없습니다.")

        if self._is_confirmed_and_not_admin(reservation, current_user):
            raise HTTPException(status_code=400, detail="확정된 예약은 변경할 수 없습니다.")

        if update_data.start_time:
            self._validate_reservation_date(update_data.start_time)

        if update_data.start_time or update_data.end_time:
            self._update_schedule(reservation, update_data, current_user)

        if update_data.requested_seats:
            reservation.requested_seats = update_data.requested_seats

        self.repository.commit()
        self.repository.refresh(reservation)
        return reservation

    def delete_reservation(self, reservation_id: int, current_user: User):
        reservation = self._get_reservation_or_404(reservation_id)

        if not self._can_modify_reservation(reservation, current_user):
            raise HTTPException(status_code=403, detail="다른 사용자의 예약을 삭제할 수 없습니다.")

        if self._is_confirmed_and_not_admin(reservation, current_user):
            raise HTTPException(status_code=400, detail="확정된 예약은 삭제할 수 없습니다.")

        self.repository.delete(reservation)

    def _get_reservation_or_404(self, reservation_id: int) -> Reservation:
        reservation = self.repository.get_reservation_by_id(reservation_id)
        if not reservation:
            raise HTTPException(status_code=404, detail="예약이 존재하지 않습니다.")
        return reservation

    def _validate_reservation_date(self, start_time: datetime):
        if start_time <= datetime.now() + timedelta(days=3):
            raise HTTPException(status_code=400, detail="예약은 시험 3일 전까지만 가능합니다.")

    def _validate_available_seats(self, exam_schedule: ExamSchedule, requested_seats: int):
        confirmed_seats = sum(
            r.requested_seats
            for r in exam_schedule.reservations
            if r.status == ReservationStatus.CONFIRMED
        )

        if confirmed_seats + requested_seats > exam_schedule.max_seats:
            raise HTTPException(status_code=400, detail="충분한 자리가 없습니다.")

    def _can_modify_reservation(self, reservation: Reservation, user: User) -> bool:
        return user.role == UserRole.ADMIN or reservation.user_id == user.id

    def _is_confirmed_and_not_admin(self, reservation: Reservation, user: User) -> bool:
        return user.role != UserRole.ADMIN and reservation.status == ReservationStatus.CONFIRMED

    def _update_schedule(self, reservation: Reservation, update_data: ReservationUpdate, user: User):
        new_start = update_data.start_time or reservation.exam_schedule.start_time
        new_end = update_data.end_time or reservation.exam_schedule.end_time

        if user.role != UserRole.ADMIN:
            self._check_seat_availability(reservation, new_start, new_end)

        reservation.exam_schedule.start_time = new_start
        reservation.exam_schedule.end_time = new_end

    def _check_seat_availability(self, reservation: Reservation, new_start: datetime, new_end: datetime):
        overlapping_seats = (
                self.repository.db.query(func.sum(Reservation.requested_seats))
                .join(ExamSchedule)
                .filter(
                    ExamSchedule.start_time < new_end,
                    ExamSchedule.end_time > new_start,
                    Reservation.status == ReservationStatus.CONFIRMED,
                    Reservation.id != reservation.id
                )
                .scalar() or 0
        )

        new_seats = reservation.requested_seats
        if overlapping_seats + new_seats > reservation.exam_schedule.max_seats:
            raise HTTPException(status_code=400, detail="해당 시간에 충분한 자리가 없습니다.")
