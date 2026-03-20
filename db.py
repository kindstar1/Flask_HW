import atexit
import datetime
import os

from dotenv import load_dotenv
from sqlalchemy import DateTime, Integer, String, Text, ForeignKey, create_engine, func
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column, sessionmaker, relationship

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "kindstar")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_DB = os.getenv("POSTGRES_DB", "flaskhw_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")

PG_DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):

    @property
    def id_dict(self):
        return {"id": self.id}

class Ad(Base):
    __tablename__ = "ads"

    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    title: MappedColumn[str] = mapped_column(String, nullable=False)
    description: MappedColumn[str] = mapped_column(String, nullable=True)
    created_at: MappedColumn[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: MappedColumn[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="ads")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": int(self.created_at.timestamp()) if self.created_at else None,
            "owner": self.user.name
    
        }

class User(Base):
    __tablename__ = "users"
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    name: MappedColumn[str] = mapped_column(String(100), nullable=False)
    email: MappedColumn[str] = mapped_column(String(100), nullable=False)
    password_hash: MappedColumn[str] = mapped_column(String(512), nullable=False)
    ads = relationship("Ad", back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name
        }

Base.metadata.create_all(engine)
atexit.register(engine.dispose)
