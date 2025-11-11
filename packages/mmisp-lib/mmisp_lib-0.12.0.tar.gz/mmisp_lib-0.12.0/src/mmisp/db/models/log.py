from datetime import datetime
from typing import Self

from sqlalchemy import DateTime, Integer, String, Text

from mmisp.db.mypy import Mapped, mapped_column

from ..database import Base


class Log(Base):
    """
    A python class representation of the database model for logs in MISP.

    Further explanation for some of the central attributes of the database model:
    - Action: Describes the action that was logged, e.g. a login or workflow execution
    - Change: A string-representation of the changes made to the logged object or of
              central information about the logged object.
    """

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str | None] = mapped_column(Text)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    model: Mapped[str] = mapped_column(String(80))
    model_id: Mapped[int] = mapped_column(Integer)
    action: Mapped[str] = mapped_column(String(20))
    user_id: Mapped[int] = mapped_column(Integer)
    change: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str] = mapped_column(String(255))
    org: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    ip: Mapped[str] = mapped_column(String(45))
    __table_args__ = ({"extend_existing": True},)

    def __init__(
        self: Self,
        *,
        model: str,
        model_id: int,
        action: str,
        user_id: int,
        email: str,
        org: str,
        title: str | None = None,
        change: str | None = None,
        description: str | None = None,
        ip: str | None = None,
        created: datetime | None = None,
        **kwargs,
    ) -> None:
        if created is None:
            created = datetime.now()
        if isinstance(created, float):
            created = datetime.fromtimestamp(created)
        super().__init__(
            title=title,
            created=created,
            model=model,
            model_id=model_id,
            action=action,
            user_id=user_id,
            change=change,
            email=email,
            org=org,
            description=description,
            ip=ip,
        )
