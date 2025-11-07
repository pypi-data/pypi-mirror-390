# app/database.py
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import inspect
from typing import Annotated
from fastapi import Depends
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def init_db() -> None:
    # verifica se ja existem tabelas
    verifica = inspect(engine)
    existe_tabela = verifica.get_table_names()
    
    if not existe_tabela:
        SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]