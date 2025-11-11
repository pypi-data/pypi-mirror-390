from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class ThreatLevel(Base):
    __tablename__ = "threat_levels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))
    form_description: Mapped[str] = mapped_column(String(255))
    __table_args__ = ({"extend_existing": True},)
