from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4
from typing import List, Optional
from enum import Enum
from datetime import date, datetime


class MuscleGroup(str, Enum):
    CHEST = "chest"
    BACK = "back"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    GLUTES = "glutes"
    ABDOMINALS = "abdominals"
    CALVES = "calves"
    ADDUCTORS = "adductors"
    SHOULDERS = "shoulders"
    LEGS = "legs"
    DELTOIDS = "deltoids"


class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


class CoachCreate(SQLModel):
    complete_name: str = Field(max_length=255)
    user_name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    password: str = Field(max_length=255)
    phone: str = Field(max_length=255)


class Coach(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    complete_name: str = Field(max_length=255)
    user_name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    password_hash: str = Field(max_length=255)
    phone: Optional[str] = Field(max_length=255)

    students: List["Student"] = Relationship(back_populates="coach")
    training_plans: List["TrainingPlan"] = Relationship(back_populates="coach")


class StudentCreate(SQLModel):
    complete_name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    phone: Optional[str] = Field(max_length=255)
    birth_date: date
    observations: Optional[str] = Field(default=None, max_length=255)
    weight_kg: Optional[float] = Field(default=None)
    height_cm: Optional[float] = Field(default=None)
    arm_circumference_cm: Optional[float] = Field(default=None)
    leg_circumference_cm: Optional[float] = Field(default=None)
    chest_circumference_cm: Optional[float] = Field(default=None)
    gender: Optional[Gender] = Field(default=None)


class Student(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    complete_name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    password_hash: str = Field(max_length=255)
    phone: Optional[str] = Field(max_length=255)
    coach_id: UUID = Field(foreign_key="coach.id")

    weight_kg: Optional[float] = Field(default=None)
    height_cm: Optional[float] = Field(default=None)
    arm_circumference_cm: Optional[float] = Field(default=None)
    leg_circumference_cm: Optional[float] = Field(default=None)
    chest_circumference_cm: Optional[float] = Field(default=None)
    gender: Optional[Gender] = Field(default=None)
    birth_date: date
    created_at: datetime = Field(default_factory=datetime.now)
    observations: Optional[str] = Field(default=None, max_length=255)
    status: Optional[str] = Field(default="active", max_length=50)

    coach: Coach = Relationship(back_populates="students")
    training_plans: List["TrainingPlan"] = Relationship(back_populates="student")
    training_performances: List["TrainingPerformance"] = Relationship(back_populates="student")


class Exercise(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, max_length=255, unique=True)
    description: Optional[str] = Field(max_length=255)
    muscle_group: MuscleGroup = Field(index=True)

    training_exercise: List["TrainingExercise"] = Relationship(back_populates="exercise")
    training_performances: List["TrainingPerformance"] = Relationship(back_populates="exercise")


class TrainingPlan(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str

    coach_id: UUID = Field(foreign_key="coach.id")
    student_id: UUID = Field(foreign_key="student.id")

    trainings: List["Training"] = Relationship(back_populates="training_plan")
    training_performances: List["TrainingPerformance"] = Relationship(back_populates="training_plan")

    coach: Coach = Relationship(back_populates="training_plans")
    student: Student = Relationship(back_populates="training_plans")


class Training(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    training_plan_id: UUID = Field(foreign_key="trainingplan.id")

    training_plan: TrainingPlan = Relationship(back_populates="trainings")
    training_exercise: List["TrainingExercise"] = Relationship(back_populates="training")

    training_performances: List["TrainingPerformance"] = Relationship(back_populates="training")


class TrainingExercise(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    training_id: UUID = Field(foreign_key="training.id")
    exercise_id: UUID = Field(foreign_key="exercise.id")
    sets: Optional[int] = None
    reps: str = Field(max_length=3)
    rir: str = Field(max_length=3)
    suggested_weight: Optional[float] = None

    training: Training = Relationship(back_populates="training_exercise")
    exercise: Exercise = Relationship(back_populates="training_exercise")

    training_performances: List["TrainingPerformance"] = Relationship(back_populates="training_exercise")


class TrainingPerformance(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    student_id: UUID = Field(foreign_key="student.id")
    training_plan_id: UUID = Field(foreign_key="trainingplan.id")
    training_id: UUID = Field(foreign_key="training.id")
    exercise_id: UUID = Field(foreign_key="exercise.id")

    training_exercise_id: Optional[UUID] = Field(default=None, foreign_key="trainingexercise.id")

    date: datetime = Field(default_factory=datetime.today)
    real_weight: Optional[float] = None
    sets: Optional[int] = None
    real_reps: Optional[int] = None
    real_rir: Optional[int] = None

    student: Student = Relationship(back_populates="training_performances")
    training_plan: TrainingPlan = Relationship(back_populates="training_performances")
    training: Training = Relationship(back_populates="training_performances")
    exercise: Exercise = Relationship(back_populates="training_performances")
    training_exercise: Optional["TrainingExercise"] = Relationship(back_populates="training_performances")