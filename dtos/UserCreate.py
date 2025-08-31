from sqlmodel import SQLModel


class UserCreate(SQLModel):
    username: str
    master_password: str
