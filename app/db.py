import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401  (registra todos los modelos en el metadata)

load_dotenv()

engine = create_engine(os.environ["DATABASE_URL"], echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
