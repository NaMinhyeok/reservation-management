# FastAPI Project API 문서
Version: 0.1.0


# 시험 일정 예약 시스템 API

프로그래머스 온라인 시험 플랫폼의 시험 일정 예약을 위한 API 시스템입니다.

## 인증

모든 API는 Authorization 헤더가 필요합니다:
- 관리자: `Bearer admin`
- 사용자: `Bearer userX` (X는 사용자 ID)


## API Endpoints
### reservations

#### POST /reservations/
Create Reservation

**Parameters:**

- authorization (header): 

**Request Body:**

Content-Type: application/json

Schema:
```json
{
  "$ref": "#/components/schemas/CreateReservationRequest"
}
```

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

#### GET /reservations/
Get Reservations

**Parameters:**

- authorization (header): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

#### PATCH /reservations/{reservation_id}/confirm
Confirm Reservation

**Parameters:**

- reservation_id (path): 
- authorization (header): 

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

#### PATCH /reservations/{reservation_id}
Update Reservation

**Parameters:**

- reservation_id (path): 
- authorization (header): 

**Request Body:**

Content-Type: application/json

Schema:
```json
{
  "$ref": "#/components/schemas/ReservationUpdate"
}
```

**Responses:**

- 200: Successful Response
- 422: Validation Error

---

#### DELETE /reservations/{reservation_id}
Delete Reservation

**Parameters:**

- reservation_id (path): 
- authorization (header): 

**Responses:**

- 204: Successful Response
- 422: Validation Error

---

### exam-schedules

#### GET /exam-schedules/available
Get Available Schedules

**Responses:**

- 200: Successful Response

---

