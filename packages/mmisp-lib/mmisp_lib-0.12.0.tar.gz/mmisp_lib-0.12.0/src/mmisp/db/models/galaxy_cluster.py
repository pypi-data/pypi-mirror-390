from typing import Optional

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mmisp.db.mixins import DictMixin, UpdateMixin
from mmisp.db.models.tag import Tag
from mmisp.db.types import DBUUID, DBListJson
from mmisp.lib.uuid import uuid

from ..database import Base


class GalaxyCluster(Base, UpdateMixin, DictMixin["GalaxyClusterDict"]):
    __tablename__ = "galaxy_clusters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(DBUUID, default=uuid, index=True)
    collection_uuid: Mapped[str] = mapped_column(DBUUID, index=True, default="")
    type: Mapped[str] = mapped_column(String(255), index=True)
    value: Mapped[str] = mapped_column(Text)
    tag_name: Mapped[str] = mapped_column(String(255), default="", index=True)
    description: Mapped[str] = mapped_column(Text)
    galaxy_id: Mapped[int] = mapped_column(Integer, ForeignKey("galaxies.id", ondelete="CASCADE"), index=True)
    source: Mapped[str] = mapped_column(String(255), default="")
    authors: Mapped[list[str]] = mapped_column(DBListJson)
    version: Mapped[int | None] = mapped_column(Integer, default=0, index=True)
    distribution: Mapped[int] = mapped_column(Integer, default=0)
    sharing_group_id: Mapped[Optional[int] | None] = mapped_column(Integer, index=True, default=None)
    org_id: Mapped[int] = mapped_column(Integer, index=True, default=0)
    orgc_id: Mapped[int] = mapped_column(Integer, index=True, default=0)
    default: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)
    extends_uuid: Mapped[str | None] = mapped_column(DBUUID, default=None, index=True)
    extends_version: Mapped[int | None] = mapped_column(Integer, index=True, default=None)
    published: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = ({"extend_existing": True},)

    org = relationship(
        "Organisation",
        primaryjoin="GalaxyCluster.org_id == Organisation.id",
        back_populates="galaxy_clusters",
        lazy="raise_on_sql",
        foreign_keys="GalaxyCluster.org_id",
    )  # type:ignore[assignment,var-annotated]
    orgc = relationship(
        "Organisation",
        primaryjoin="GalaxyCluster.orgc_id == Organisation.id",
        back_populates="galaxy_clusters_created",
        lazy="raise_on_sql",
        foreign_keys="GalaxyCluster.orgc_id",
    )  # type:ignore[assignment,var-annotated]
    galaxy = relationship(
        "Galaxy",
        back_populates="galaxy_clusters",
        lazy="raise_on_sql",
    )  # type:ignore[assignment,var-annotated]
    galaxy_elements = relationship(
        "GalaxyElement",
        back_populates="galaxy_cluster",
        lazy="raise_on_sql",
    )  # type:ignore[assignment,var-annotated]
    cluster_relations: Mapped[list["GalaxyClusterRelation"]] = relationship(
        "GalaxyClusterRelation",
        back_populates="galaxy_cluster",
        lazy="raise_on_sql",
        foreign_keys="GalaxyClusterRelation.galaxy_cluster_id",
    )
    tag = relationship(
        "Tag",
        primaryjoin="GalaxyCluster.tag_name == Tag.name",
        back_populates="galaxy_cluster",
        lazy="raise_on_sql",
        foreign_keys="GalaxyCluster.tag_name",
        single_parent=True,
        uselist=False,
    )  # type:ignore[assignment,var-annotated]


class GalaxyElement(Base, DictMixin["GalaxyElementDict"], UpdateMixin):
    __tablename__ = "galaxy_elements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    galaxy_cluster_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(GalaxyCluster.id, ondelete="CASCADE"), index=True
    )
    key: Mapped[str] = mapped_column(String(255), default="", index=True)
    value: Mapped[str] = mapped_column(Text)

    galaxy_cluster = relationship(
        "GalaxyCluster",
        back_populates="galaxy_elements",
        lazy="raise_on_sql",
    )  # type:ignore[assignment,var-annotated]


class GalaxyClusterRelationTag(Base):
    __tablename__ = "galaxy_cluster_relation_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    galaxy_cluster_relation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("galaxy_cluster_relations.id"), index=True
    )
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id"), index=True)


class GalaxyClusterRelation(Base, DictMixin["GalaxyClusterRelationDict"], UpdateMixin):
    __tablename__ = "galaxy_cluster_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    galaxy_cluster_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(GalaxyCluster.id, ondelete="CASCADE"), index=True
    )
    referenced_galaxy_cluster_id: Mapped[int] = mapped_column(Integer, index=True)
    referenced_galaxy_cluster_uuid: Mapped[str] = mapped_column(DBUUID, index=True)
    referenced_galaxy_cluster_type: Mapped[str] = mapped_column(Text)
    galaxy_cluster_uuid: Mapped[str] = mapped_column(DBUUID, index=True)
    distribution: Mapped[int] = mapped_column(Integer, default=0)
    sharing_group_id: Mapped[Optional[int] | None] = mapped_column(
        Integer, ForeignKey("sharing_groups.id"), index=True, default=None
    )
    default: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    galaxy_cluster: Mapped[GalaxyCluster] = relationship(
        "GalaxyCluster",
        back_populates="cluster_relations",
        lazy="raise_on_sql",
        foreign_keys="GalaxyClusterRelation.galaxy_cluster_id",
    )
    relation_tags: Mapped[list[Tag]] = relationship(
        "Tag", secondary=GalaxyClusterRelationTag.__table__, lazy="raise_on_sql"
    )


class GalaxyReference(Base, DictMixin["GalaxyReferenceDict"]):
    __tablename__ = "galaxy_reference"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    galaxy_cluster_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(GalaxyCluster.id, ondelete="CASCADE"), index=True
    )

    referenced_galaxy_cluster_id: Mapped[int] = mapped_column(Integer, index=True)
    referenced_galaxy_cluster_uuid: Mapped[str] = mapped_column(DBUUID, index=True)
    referenced_galaxy_cluster_type: Mapped[str] = mapped_column(Text)
    referenced_galaxy_cluster_value: Mapped[str] = mapped_column(Text)
