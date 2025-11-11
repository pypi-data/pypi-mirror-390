from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Taxonomy(Base):
    __tablename__ = "taxonomies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    namespace: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    exclusive: Mapped[Optional[bool] | None] = mapped_column(Boolean, default=False)
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    highlighted: Mapped[Optional[bool] | None] = mapped_column(Boolean, default=False)

    predicates: Mapped[list["TaxonomyPredicate"]] = relationship(
        "TaxonomyPredicate", back_populates="taxonomy", lazy="raise_on_sql"
    )


class TaxonomyPredicate(Base):
    __tablename__ = "taxonomy_predicates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    taxonomy_id: Mapped[int] = mapped_column(Integer, ForeignKey(Taxonomy.id, ondelete="CASCADE"), index=True)
    value: Mapped[str] = mapped_column(Text)
    expanded: Mapped[Optional[str] | None] = mapped_column(Text)
    colour: Mapped[Optional[str] | None] = mapped_column(String(7))
    description: Mapped[Optional[str] | None] = mapped_column(Text)
    exclusive: Mapped[Optional[bool] | None] = mapped_column(Boolean, default=False)
    numerical_value: Mapped[Optional[int] | None] = mapped_column(Integer, index=True)

    taxonomy: Mapped[Taxonomy] = relationship(Taxonomy, back_populates="predicates", lazy="raise_on_sql")
    entries: Mapped[list["TaxonomyEntry"]] = relationship(
        "TaxonomyEntry", back_populates="predicate", lazy="raise_on_sql"
    )


class TaxonomyEntry(Base):
    __tablename__ = "taxonomy_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    taxonomy_predicate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(TaxonomyPredicate.id, ondelete="CASCADE"), index=True
    )
    value: Mapped[str] = mapped_column(Text)
    expanded: Mapped[Optional[str] | None] = mapped_column(Text)
    colour: Mapped[Optional[str] | None] = mapped_column(String(7))
    description: Mapped[Optional[str] | None] = mapped_column(Text)
    numerical_value: Mapped[Optional[int] | None] = mapped_column(Integer, index=True)

    predicate: Mapped[TaxonomyPredicate] = relationship(
        TaxonomyPredicate, back_populates="entries", lazy="raise_on_sql"
    )
