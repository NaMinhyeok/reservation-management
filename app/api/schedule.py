from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repository.schedule import ExamScheduleRepository
from app.schemas.schedule import AvailableExamScheduleResponse
from app.service.schedule import ExamScheduleService

router = APIRouter(prefix="/exam-schedules", tags=["exam-schedules"])


@router.get("/available", response_model=List[AvailableExamScheduleResponse])
async def get_available_schedules(db: Session = Depends(get_db)):
    repository = ExamScheduleRepository(db)
    service = ExamScheduleService(repository)
    return service.get_available_schedules()
