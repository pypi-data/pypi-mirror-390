from sqlalchemy import Boolean, ForeignKey, Integer, String

from mmisp.db.database import Base
from mmisp.db.mypy import Mapped, mapped_column


class Warninglist(Base):
    __tablename__ = "warninglists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(255), default="string")
    description: Mapped[str] = mapped_column(String(255))
    version: Mapped[int] = mapped_column(Integer, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    default: Mapped[bool] = mapped_column(Boolean, default=True)
    category: Mapped[str] = mapped_column(String(255))
    __table_args__ = ({"extend_existing": True},)


class WarninglistEntry(Base):
    __tablename__ = "warninglist_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(String(255))
    warninglist_id: Mapped[int] = mapped_column(Integer, ForeignKey(Warninglist.id, ondelete="CASCADE"))
    comment: Mapped[str | None] = mapped_column(String(255))
    __table_args__ = ({"extend_existing": True},)


class WarninglistType(Base):
    __tablename__ = "warninglist_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(255))
    warninglist_id: Mapped[int] = mapped_column(Integer, ForeignKey(Warninglist.id, ondelete="CASCADE"))
