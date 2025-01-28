from fastapi import HTTPException

from app.core.transaction import transactional
from app.models import User, ExamSchedule, Reservation
from app.models.enums import UserRole, ReservationStatus
from app.repository.reservation import ReservationRepository
from app.schemas.reservation import ReservationUpdate, CreateReservationRequest


class ReservationService:
    def __init__(self, repository: ReservationRepository):
        self.repository = repository

    @transactional
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

        return self.repository.save(new_reservation)

    @transactional
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
        return self.repository.save(reservation)

    @transactional
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

        return self.repository.save(reservation)

    @transactional
    def delete_reservation(self, reservation_id: int, current_user: User):
        reservation = self._get_reservation_or_404(reservation_id)

        if not self._can_modify_reservation(reservation, current_user):
            raise HTTPException(status_code=403, detail="다른 사용자의 예약을 삭제할 수 없습니다.")

        if self._is_confirmed_and_not_admin(reservation, current_user):
            raise HTTPException(status_code=400, detail="확정된 예약은 삭제할 수 없습니다.")

        self.repository.delete(reservation)
