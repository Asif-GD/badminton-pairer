"""
Models serve as a blueprint of the table in the database.
"""

from sqlalchemy import String, PickleType
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# SQLAlchemy 2.0 style
class Base(DeclarativeBase):
    pass


class Pair(Base):
    __tablename__ = "pairs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(160), unique=True)

    player_list: Mapped[list] = mapped_column(MutableList.as_mutable(PickleType), default=[])

    benched_player: Mapped[list] = mapped_column(MutableList.as_mutable(PickleType), default=[])
    lucky_player: Mapped[list] = mapped_column(MutableList.as_mutable(PickleType), default=[])
    seventh_player: Mapped[str] = mapped_column(String(80), default="")
