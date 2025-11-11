from sqlalchemy import Boolean, Integer, String, Text

from mmisp.db.mypy import Mapped, mapped_column

from ..database import Base


class WorkflowBlueprint(Base):
    """
    A python class representation of the database model for blueprints of workflows in MISP.

    The most attributes of this model are similar to the attributes of workflows,
    except the attributes "enabled", "counter", "trigger_id" and "debug_enabled", because these
    attributes are not useful or sensible for blueprints.

    Also, the attribute "default" is added, which is a boolean clarifying whether the blueprint
    is a default MISP blueprint.
    """

    __tablename__ = "workflow_blueprints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # primary_key ??
    uuid: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(191))
    description: Mapped[str] = mapped_column(String(191))
    timestamp: Mapped[int] = mapped_column(Integer, default=0)
    default: Mapped[bool] = mapped_column(Boolean, default=False)  # TODO: technically tinyint(1)
    data: Mapped[str | None] = mapped_column(Text)
