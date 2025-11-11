from datetime import datetime
from typing import Self

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped

from mmisp.db.mixins import DictMixin, UpdateMixin
from mmisp.db.mypy import mapped_column
from mmisp.lib.permissions import Permission

from ..database import Base

RoleAttrs = {
    "__tablename__": "roles",
    "id": mapped_column(Integer, primary_key=True),
    "name": mapped_column(String(255)),
    "created": mapped_column(DateTime, default=None),
    "modified": mapped_column(DateTime, default=None),
    "default_role": mapped_column(Boolean, default=False),
    "memory_limit": mapped_column(String(255), default=""),
    "max_execution_time": mapped_column(String(255), default=""),
    "restricted_to_site_admin": mapped_column(Boolean, default=False),
    # This line was added as part of task MMISP-3033
    "restsearch_limit_result": mapped_column(Integer, default=0),
    "enforce_rate_limit": mapped_column(Boolean, default=False),
    "rate_limit_count": mapped_column(Integer, default=0),
} | {f"perm_{x.value}": mapped_column(Boolean, default=False) for x in Permission}

RoleAttrs["__annotations__"] = (
    {
        "id": Mapped[int],
        "name": Mapped[str],
        "created": Mapped[datetime | None],
        "modified": Mapped[datetime | None],
        "default_role": Mapped[bool],
        "memory_limit": Mapped[str | None],
        "max_execution_time": Mapped[str | None],
        "restricted_to_site_admin": Mapped[bool],
        "enforce_rate_limit": Mapped[bool],
        "rate_limit_count": Mapped[bool],
    }
    | {f"perm_{x.value}": Mapped[bool] for x in Permission}
    | {  # just the way it is ¯\_(ツ)_/¯
        "perm_add": Mapped[bool | None],
        "perm_modify": Mapped[bool | None],
        "perm_modify_org": Mapped[bool | None],
        "perm_publish": Mapped[bool | None],
        "perm_sync": Mapped[bool | None],
        "perm_admin": Mapped[bool | None],
        "perm_audit": Mapped[bool | None],
        "perm_full": Mapped[bool | None],
    }
)

RoleModel = type("RoleModel", (Base,), RoleAttrs)


class Role(RoleModel, UpdateMixin, DictMixin["RoleDict"]):  # type:ignore[misc,valid-type]
    def get_permissions(self: Self) -> set[Permission]:
        d: list[Permission] = []

        for key in self.__mapper__.c.keys():
            if key.startswith("perm_") and getattr(self, key):
                d.append(Permission(key[len("perm_") :]))

        return set(d)

    def check_permission(self: Self, permission: Permission) -> bool:
        """
        Checks whether the role has the specified permission

        args:
            self: the role itself
            permission: the permission to check

        returns:
            true if role has permission
        """
        return getattr(self, "perm_" + permission.value)

    @hybrid_property
    def permission(self: Self) -> str:
        if self.perm_add and self.perm_modify and self.perm_publish:
            return "3"
        elif self.perm_add and self.perm_modify_org:
            return "2"
        elif self.perm_add and self.perm_modify:
            return "1"
        return "0"

    @hybrid_property
    def permission_description(self: Self) -> str:
        if self.perm_add and self.perm_modify and self.perm_publish:
            return "publish"
        elif self.perm_add and self.perm_modify_org:
            return "manage_org"
        elif self.perm_add and self.perm_modify:
            return "manage_own"
        return "read_only"
