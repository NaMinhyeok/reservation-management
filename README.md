# 시험 일정 예약 시스템

프로그래머스 온라인 시험 플랫폼의 시험 일정 예약을 위한 API 시스템입니다.

## 기술 스택
- Python 3.9+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic

## 환경 설정

### 1. 저장소 클론
```bash
git clone https://github.com/NaMinhyeok/reservation-management.git
cd reservation-management
```

### 2. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
`.env` 파일을 프로젝트 루트 디렉토리에 생성하고 다음 내용을 입력합니다:

```env
POSTGRES_USER=your_user_name
POSTGRES_PASSWORD=your_password
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=reservation
```

### 5. 데이터베이스 설정
PostgreSQL이 설치되어 있어야 합니다.

```bash
# PostgreSQL 서버 실행
# Linux
sudo service postgresql start
# Mac
brew services start postgresql
# Windows
# PostgreSQL이 서비스로 실행됩니다.

# 데이터베이스 생성
createdb reservation
```

## 실행 방법

### 개발 서버 실행
```bash
uvicorn app.main:app --reload
```

서버가 시작되면 `http://localhost:8000` 에서 API가 실행됩니다.

## API 테스트

### Swagger UI
- `http://localhost:8000/docs` 에서 API 문서와 테스트 인터페이스를 확인할 수 있습니다.

### 인증
모든 API는 Authorization 헤더가 필요합니다:
- 관리자: `Bearer admin`
- 사용자: `Bearer userX` (X는 사용자 ID)

예시:
```bash
curl -X GET "http://localhost:8000/api/exam-schedules/available" \
     -H "Authorization: Bearer admin"
```

## 테스트 데이터
서버 시작 시 자동으로 테스트 데이터가 생성됩니다:
- 관리자 계정
- 테스트 사용자 계정
- 샘플 시험 일정
- 샘플 예약