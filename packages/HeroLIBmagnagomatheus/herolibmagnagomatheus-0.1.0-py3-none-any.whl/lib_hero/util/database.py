# app/database.py
from sqlmodel import SQLModel, Session, create_engine
from typing import Annotated
from fastapi import Depends
import os

connect_args = {"check_same_thread": False}
engine = create_engine("sqlite:///:memory:" , echo=False, connect_args=connect_args)

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]