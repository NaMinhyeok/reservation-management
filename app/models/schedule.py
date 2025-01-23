from datetime import datetime

from sqlalchemy import DateTime, Column, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class ExamSchedule(Base):
    __tablename__ = "exam_schedules"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    max_seats = Column(Integer, nullable=False, default=50000)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    reservations = relationship("Reservation", back_populates="exam_schedule")
