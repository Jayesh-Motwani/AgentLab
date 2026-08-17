import os
import sqlmodel
from sqlmodel import Session, SQLModel

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:  # Empty string evaluates to false
    raise NotImplementedError("\'DATABASE_URL\' cannot be empty")

engine = sqlmodel.create_engine(DATABASE_URL)

# database models


def init_db():
    print("creating database tables")
    # Make sure db exists, if not then initialize
    SQLModel.metadata.create_all(engine)

# API routes


def get_session():
    with Session(engine) as session:
        yield session
