"""
Models serve as a blueprint of the table in the database.
"""
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Pair(Base):
    __tablename__ = "pairs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(160), unique=True)

    benched_player: Mapped[str] = mapped_column(String(80))
