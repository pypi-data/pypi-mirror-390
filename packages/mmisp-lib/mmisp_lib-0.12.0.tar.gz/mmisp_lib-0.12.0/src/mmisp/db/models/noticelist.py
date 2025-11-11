from sqlalchemy import Boolean, ForeignKey, Integer, String, Text

from mmisp.db.database import Base
from mmisp.db.mypy import Mapped, mapped_column


class Noticelist(Base):
    __tablename__ = "noticelists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    expanded_name: Mapped[str] = mapped_column(String(255))
    ref: Mapped[str | None] = mapped_column(String(255))  # data serialized as json
    geographical_area: Mapped[str | None] = mapped_column(String(255))  # data serialized as json
    version: Mapped[int] = mapped_column(Integer, default=1)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = ({"extend_existing": True},)


class NoticelistEntry(Base):
    __tablename__ = "noticelist_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    noticelist_id: Mapped[int] = mapped_column(Integer, ForeignKey(Noticelist.id, ondelete="CASCADE"))
    data: Mapped[str] = mapped_column(Text)  # data serialized as json
