from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import User, ExamSchedule, Reservation
from app.models.enums import UserRole, ReservationStatus


def create_seed_data(db: Session):
    if db.query(User).first() is not None:
        return

    admin = User(
        name="Admin",
        password="비밀번호 예시",
        role=UserRole.ADMIN
    )
    users = [
        User(name=f"테스트 유저 {i}",
             password=f"비밀번호_예시_{i + 2}",
             role=UserRole.USER)
        for i in range(3)
    ]
    db.add(admin)
    db.add_all(users)
    db.commit()

    now = datetime.now()
    schedules = [
        ExamSchedule(
            start_time=now + timedelta(days=7 + i * 7, hours=9),
            end_time=now + timedelta(days=7 + i * 7, hours=11),
            max_seats=50000
        )
        for i in range(3)
    ]
    db.add_all(schedules)
    db.commit()

    reservations = [
        Reservation(
            user_id=2,
            exam_id=1,
            status=ReservationStatus.CONFIRMED,
            requested_seats=20000
        ),
        Reservation(
            user_id=2,
            exam_id=2,
            status=ReservationStatus.PENDING,
            requested_seats=15000
        ),
        Reservation(
            user_id=3,
            exam_id=3,
            status=ReservationStatus.CANCELLED,
            requested_seats=10000
        )
    ]
    db.add_all(reservations)
    db.commit()