from sqlalchemy import DateTime, Integer, Text, text
from sqlalchemy.dialects.mysql import INTEGER

from mmisp.db.mypy import Mapped, mapped_column

from ..database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date_created: Mapped[DateTime] = mapped_column(DateTime)
    date_modified: Mapped[DateTime] = mapped_column(DateTime)
    user_id: Mapped[int] = mapped_column(INTEGER)
    contents: Mapped[str] = mapped_column(Text)
    post_id: Mapped[int] = mapped_column(INTEGER, index=True, server_default=text("0"))
    thread_id: Mapped[int] = mapped_column(INTEGER, index=True, server_default=text("0"))
