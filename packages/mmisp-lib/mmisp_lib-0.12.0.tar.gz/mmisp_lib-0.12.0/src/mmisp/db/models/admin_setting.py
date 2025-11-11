from sqlalchemy import Index, Text, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class AdminSetting(Base):
    """
    A python class representation of the database model for admin settings in MISP
    """

    __tablename__ = "admin_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    setting: Mapped[str] = mapped_column(String(255))

    value: Mapped[str] = mapped_column(Text)

    __table_args__ = (Index("setting", "setting", unique=True),)
