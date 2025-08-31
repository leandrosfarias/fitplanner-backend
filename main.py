from contextlib import asynccontextmanager

from passlib.context import CryptContext
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

import models
from models import Coach
from sqlmodel import SQLModel, Session, select

from DbManager import engine
from auth import create_access_token, verify_password, get_password_hash


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


def get_session() -> Session:
    with Session(engine) as session:
        yield session


@app.post("/coach/", status_code=status.HTTP_201_CREATED)
async def create_coach(coach: models.CoachCreate,
                       session: Session = Depends(get_session)):
    hashed_password = get_password_hash(coach.password)

    db_coach = models.Coach(
        **coach.dict(exclude={"password"}),
        password_hash=hashed_password
    )

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


@app.post("/coach/login/")
async def perform_login_coach(form_data: OAuth2PasswordRequestForm = Depends(),
                              session: Session = Depends(get_session)):
    username = form_data.username
    password = form_data.password

    coach: Coach | None = session.exec(
            select(Coach)
            .where(Coach.user_name == username)
        ).first()
    print('Coach -> ', coach)
    if coach and verify_password(password, coach.password_hash):
        access_token = create_access_token(data={"sub": str(coach.id)})
        return {
            "access_token": access_token,
            "coach_id": str(coach.id)
        }
