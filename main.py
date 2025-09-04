from contextlib import asynccontextmanager
from typing import List

from passlib.context import CryptContext
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

import models
from models import Coach
from sqlmodel import SQLModel, Session, select

from DbManager import engine, get_coach_by_id
from auth import create_access_token, verify_password, get_password_hash, get_current_user_id
from fastapi.middleware.cors import CORSMiddleware


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

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/coach/{coach_id}")
async def get_coach(coach_id: str, session: Session = Depends(get_session)):
    coach = await get_coach_by_id(coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    return coach


@app.post("/coach/login/")
async def perform_login_coach(form_data: OAuth2PasswordRequestForm = Depends(),
                              session: Session = Depends(get_session)):
    email = form_data.username
    password = form_data.password

    coach: Coach | None = session.exec(
            select(Coach)
            .where(Coach.email == email)
        ).first()

    if coach is None:
        print('Coach -> ', coach)
        raise HTTPException(status_code=404, detail="Invalid email or password")

    if coach and verify_password(password, coach.password_hash):
        access_token = create_access_token(data={"sub": str(coach.id)})
        return {
            "access_token": access_token,
            "coach_id": str(coach.id),
            "email": coach.email,
            "username": coach.user_name
        }


@app.post("/student")
def create_student(studentCreate: models.StudentCreate,
                   session: Session = Depends(get_session),
                   current_coach_id: str = Depends(get_current_user_id)):
    if not current_coach_id:
        raise HTTPException(status_code=401, detail="Not authorized")

    db_student = select(models.Student).where(models.Student.complete_name == studentCreate.complete_name)
    existing_student = session.exec(db_student).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Student already exists")
    students_dict = studentCreate.dict()
    has_pwd = get_password_hash(str(studentCreate.birth_date.year))
    students_dict["password_hash"] = has_pwd
    students_dict["coach_id"] = current_coach_id
    db_student = models.Student(**students_dict)
    try:
        session.add(db_student)
        session.commit()
        session.refresh(db_student)
        return db_student.dict(exclude={"password_hash", "coach_id"})
    except Exception as e:
        session.rollback()
        print(f"Error creating student: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to create student: {e}")


@app.get("/students", response_model=List[models.Student])
def get_students(session: Session = Depends(get_session),
                 current_coach_id: str = Depends(get_current_user_id)):
    if not current_coach_id:
        raise HTTPException(status_code=401, detail="Not authorized")

    students = session.exec(
        select(models.Student).where(models.Student.coach_id == current_coach_id)
    ).all()
    return students
