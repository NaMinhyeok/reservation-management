from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models import User
from app.models.enums import UserRole
from app.repository.reservation import ReservationRepository
from app.schemas.reservation import ReservationResponse, ReservationUpdate, CreateReservationRequest
from app.service.reservation import ReservationService

router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.post("/", response_model=ReservationResponse)
def create_reservation(
        request: CreateReservationRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    repository = ReservationRepository(db)
    service = ReservationService(repository)
    return service.create_reservation(request, current_user)


@router.get("/", response_model=List[ReservationResponse])
def get_reservations(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    repository = ReservationRepository(db)
    if current_user.role == UserRole.ADMIN:
        return repository.get_all_reservations()
    return repository.get_user_reservations(current_user.id)


@router.patch("/{reservation_id}/confirm", response_model=ReservationResponse)
async def confirm_reservation(
        reservation_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    repository = ReservationRepository(db)
    service = ReservationService(repository)
    return service.confirm_reservation(reservation_id, current_user)


@router.patch("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
        reservation_id: int,
        update_data: ReservationUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    repository = ReservationRepository(db)
    service = ReservationService(repository)
    return service.update_reservation(reservation_id, update_data, current_user)


@router.delete("/{reservation_id}", status_code=204)
async def delete_reservation(
        reservation_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    repository = ReservationRepository(db)
    service = ReservationService(repository)
    service.delete_reservation(reservation_id, current_user)
