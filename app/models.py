from sqlmodel import Field, Session, SQLModel, create_engine, Relationship
from typing import Annotated, Optional, List
from fastapi import Depends
from datetime import datetime
from sqlalchemy.sql import func
from pwdlib import PasswordHash
from .config import settings


SQLMODEL_URL = (f'postgresql+psycopg://{settings.database_username}:{settings.database_password}@'
                f'{settings.database_hostname}:{settings.database_port}/{settings.database_name}')
engine = create_engine(SQLMODEL_URL)
pwd_hash = PasswordHash.recommended()



class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(nullable=False, primary_key=True)
    email: str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    created_at: datetime = Field(sa_column_kwargs={"server_default": func.now()}, nullable=False)
    posts: List["Post"] = Relationship(back_populates="owner")


class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: int = Field(nullable=False, primary_key=True)
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    published: bool = Field(sa_column_kwargs={"server_default": "TRUE"}, nullable=False)
    created_at: datetime = Field(sa_column_kwargs={"server_default": func.now()}, nullable=False)
    owner_id: int = Field(nullable=False, foreign_key="users.id", ondelete="CASCADE")
    owner: Optional[User] = Relationship(back_populates="posts")


class Vote(SQLModel, table=True):
    __tablename__ = "votes"

    user_id: int = Field(nullable=False, foreign_key="users.id", primary_key=True, ondelete="CASCADE")
    post_id: int = Field(nullable=False, foreign_key="posts.id", primary_key=True, ondelete="CASCADE")
    # post: Post = Relationship(back_populates="votes")
    # user: User = Relationship(back_populates="votes")

def create_table():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def get_password_hash(password: str):
    return pwd_hash.hash(password)

def verify(plain_password: str, hashed_password: str):
    return pwd_hash.verify(plain_password, hashed_password)


SessionDep = Annotated[Session, Depends(get_session)]


# Connecting to database using Postgres driver

# from psycopg.rows import dict_row
# import psycopg
# import time
# while True:
#     try:
#         conn = psycopg.connect(host=settings.database_hostname,
#                              dbname=settings.database_name,
#                              user=settings_database_username,
#                              password=settings_database_password,
#                              row_factory=dict_row)
#         cur = conn.cursor()
#         print("Database connection was successful")
#         break
#     except Exception as error:
#         print("Connecting to database failed")
#         print("Error: ", error)
#         time.sleep(2)
