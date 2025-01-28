from fastapi import FastAPI

from app.api import reservation, schedule
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.core.dummy import create_seed_data
from app.docs.description import API_DESCRIPTION, TAGS_METADATA

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=API_DESCRIPTION,
    openapi_tags=TAGS_METADATA,
)


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        create_seed_data(db)
    finally:
        db.close()


app.include_router(reservation.router)
app.include_router(schedule.router)
