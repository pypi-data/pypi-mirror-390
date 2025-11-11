from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import relationship

from mmisp.db.database import Base
from mmisp.db.mixins import DictMixin, UpdateMixin
from mmisp.db.mypy import Mapped, mapped_column


class Tag(Base, UpdateMixin, DictMixin["TagDict"]):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    colour: Mapped[int] = mapped_column(String(7))
    exportable: Mapped[bool] = mapped_column(Boolean)
    org_id: Mapped[int] = mapped_column(Integer, default=0, index=True)
    user_id: Mapped[int] = mapped_column(Integer, default=0, index=True)
    hide_tag: Mapped[bool] = mapped_column(Boolean, default=False)
    numerical_value: Mapped[int | None] = mapped_column(Integer, index=True)
    is_galaxy: Mapped[bool] = mapped_column(Boolean, default=False)
    is_custom_galaxy: Mapped[bool] = mapped_column(Boolean, default=False)
    local_only: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = ({"extend_existing": True},)

    attributetags = relationship("AttributeTag", back_populates="tag", lazy="raise_on_sql", viewonly=True)
    eventtags = relationship("EventTag", back_populates="tag", lazy="raise_on_sql", viewonly=True)
    galaxy_cluster = relationship(
        "GalaxyCluster",
        primaryjoin="Tag.name == GalaxyCluster.tag_name",
        back_populates="tag",
        lazy="raise_on_sql",
        foreign_keys="GalaxyCluster.tag_name",
        single_parent=True,
        uselist=False,
    )  # type:ignore[assignment,var-annotated]
