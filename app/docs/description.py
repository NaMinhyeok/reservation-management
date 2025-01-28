API_DESCRIPTION = """
# 시험 일정 예약 시스템 API

프로그래머스 온라인 시험 플랫폼의 시험 일정 예약을 위한 API 시스템입니다.

## 인증

모든 API는 Authorization 헤더가 필요합니다:
- 관리자: `Bearer admin`
- 사용자: `Bearer userX` (X는 사용자 ID)
"""

TAGS_METADATA = [
    {
        "name": "exam-schedules",
        "description": "시험 일정 조회 및 관리를 위한 엔드포인트",
    },
    {
        "name": "reservations",
        "description": "예약 생성, 수정, 삭제 및 조회를 위한 엔드포인트",
    },
]

# app/docs/examples.py
RESERVATION_EXAMPLES = {
    "normal_response": {
        "id": 1,
        "user_id": 2,
        "exam_id": 1,
        "status": "pending",
        "requested_seats": 1000,
        "created_at": "2024-01-28T10:00:00",
        "updated_at": "2024-01-28T10:00:00"
    },
    "error_response": {
        "detail": "충분한 자리가 없습니다."
    }
}