from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.core.dummy import create_seed_data

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        create_seed_data(db)
    finally:
        db.close()
