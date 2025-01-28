from datetime import datetime, timedelta

from app.core.transaction import transactional
from app.repository.schedule import ExamScheduleRepository
from app.schemas.schedule import AvailableExamScheduleResponse

class ExamScheduleService:
    def __init__(self, repository: ExamScheduleRepository):
        self.repository = repository

    @transactional
    def get_available_schedules(self) -> list[AvailableExamScheduleResponse]:
        min_available_date = datetime.now() + timedelta(days=3)
        schedules = self.repository.find_available_schedules(min_available_date)

        return [
            AvailableExamScheduleResponse(
                **schedule.__dict__,
                available_seats=schedule.max_seats - self.repository.get_confirmed_seats_count(schedule)
            )
            for schedule in schedules
        ]
