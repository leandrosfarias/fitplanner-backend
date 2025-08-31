from contextlib import asynccontextmanager

from passlib.context import CryptContext
from fastapi import FastAPI, HTTPException, status

import models
from sqlmodel import SQLModel, Session

from DbManager import engine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_db_and_tables():
    print("Criando tabelas...")
    SQLModel.metadata.create_all(engine)
    print("Tabelas criadas com sucesso!")


def drop_db_and_tables():
    print("Droppando tabelas...")
    SQLModel.metadata.drop_all(engine)
    print("Tabelas droppadas com sucesso!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    drop_db_and_tables()


app = FastAPI(lifespan=lifespan)


@app.post("/coach/", status_code=status.HTTP_201_CREATED)
async def create_coach(coach: models.CoachCreate):
    hashed_password = pwd_context.hash(coach.password)

    db_coach = models.Coach(
        **coach.dict(exclude={"password"}),
        password_hash=hashed_password

    )

    with Session(engine) as session:
        try:
            session.add(db_coach)
            session.commit()
            session.refresh(db_coach)
            response = db_coach.dict(exclude={"password_hash"})
            return response
        except Exception as e:
            session.rollback()
            print(f"Error creating coach: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to create coach: {e}")
