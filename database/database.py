import os.path
from typing import Final, Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from database.models import Base

BASE_DIR: Final[str] = os.path.dirname(os.path.abspath(__file__))
sqlite_file_name = "pair-app.db"
sqlite_db_url = f"sqlite+pysqlite:///{BASE_DIR}/{sqlite_file_name}"

# since it's normally okay to use same thread for multiple requests in FastAPI
connect_args = {"check_same_thread": False}
engine = create_engine(
    url=sqlite_db_url,
    connect_args=connect_args,
    echo=True
)


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)


LocalSession = sessionmaker(bind=engine)


# to ONLY open a db connection upon request
def get_db_session():
    with LocalSession.begin() as db_session:
        yield db_session


SessionDependency = Annotated[Session, Depends(get_db_session)]
