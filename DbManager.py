from sqlmodel import create_engine, Session, select
import os
import models


database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(database_url)


async def get_coach_by_id(coach_id: str):
    with Session(engine) as session:
        result = session.exec(
            select(models.Coach)
            .where(models.Coach.id == coach_id))
        return result.first()
