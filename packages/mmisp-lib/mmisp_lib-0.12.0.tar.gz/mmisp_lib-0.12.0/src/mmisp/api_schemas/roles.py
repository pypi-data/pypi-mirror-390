from datetime import datetime
from typing import Self

from pydantic import BaseModel, field_serializer

from mmisp.lib.permissions import Permission


class HasPermission(BaseModel):
    perm_add: bool | None = None
    perm_modify: bool | None = None
    perm_modify_org: bool | None = None
    perm_publish: bool | None = None
    perm_delegate: bool | None = None
    perm_sync: bool | None = None
    perm_admin: bool | None = None
    perm_audit: bool | None = None
    perm_auth: bool | None = None
    perm_site_admin: bool | None = None
    perm_regexp_access: bool | None = None
    perm_tagger: bool | None = None
    perm_template: bool | None = None
    perm_sharing_group: bool | None = None
    perm_tag_editor: bool | None = None
    perm_sighting: bool | None = None
    perm_object_template: bool | None = None
    perm_publish_zmq: bool | None = None
    perm_publish_kafka: bool | None = None
    perm_decaying: bool | None = None
    perm_galaxy_editor: bool | None = None
    perm_warninglist: bool | None = None
    perm_view_feed_correlations: bool | None = None
    perm_skip_otp: bool | None = None
    perm_server_sign: bool | None = None
    perm_analyst_data: bool | None = None
    perm_sync_authoritative: bool | None = None
    perm_sync_internal: bool | None = None


class Role(HasPermission):
    id: int
    name: str
    created: datetime | None = None
    modified: datetime | None = None
    default_role: bool
    memory_limit: str | None = None
    max_execution_time: str | None = None
    restricted_to_site_admin: bool
    enforce_rate_limit: bool
    rate_limit_count: int
    permission: int | None = None  # number as string
    permission_description: str | None = None

    @field_serializer("created", "modified")
    def serialize_timestamp(self: Self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")


class RoleAttributeResponse(Role):
    pass


class IndexRole(Role):
    default: bool


class RoleUsersResponse(HasPermission):
    id: int
    name: str
    created: datetime | None = None
    modified: datetime | None = None
    default_role: bool | None = None
    memory_limit: str | None = None
    max_execution_time: str | None = None
    restricted_to_site_admin: bool | None = None
    enforce_rate_limit: bool | None = None
    rate_limit_count: int | None = None

    @field_serializer("created", "modified")
    def serialize_timestamp(self: Self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")


class GetRolesResponse(BaseModel):
    Role: RoleAttributeResponse


class IndexRolesResponse(BaseModel):
    Role: IndexRole


class GetRoleResponse(BaseModel):
    Role: RoleAttributeResponse | None = None


class AddRoleBody(HasPermission):
    name: str
    default_role: bool
    memory_limit: str | None = None
    max_execution_time: str | None = None
    restricted_to_site_admin: bool
    enforce_rate_limit: bool
    rate_limit_count: int


class AddRoleResponse(BaseModel):
    Role: RoleAttributeResponse
    created: bool
    message: str


class DeleteRoleResponse(BaseModel):
    Role: RoleAttributeResponse | None = None
    saved: bool
    success: bool | None = None
    name: str
    message: str
    url: str
    id: int
    errors: str | None = None


class EditRoleBody(HasPermission):
    name: str | None = None
    default_role: bool | None = None
    memory_limit: str | None = None
    max_execution_time: str | None = None
    restricted_to_site_admin: bool | None = None
    enforce_rate_limit: bool | None = None


class EditRoleResponse(BaseModel):
    Role: RoleAttributeResponse


class ReinstateRoleResponse(BaseModel):
    Role: RoleAttributeResponse
    success: bool
    message: str
    url: str
    id: int


class FilterRoleBody(BaseModel):
    # filter can be expanded by adding more criteria to filter for
    permissions: list[Permission] | None = None


class FilterRoleResponse(BaseModel):
    Role: RoleAttributeResponse


class EditUserRoleBody(BaseModel):
    role_id: int


class EditUserRoleResponse(BaseModel):
    saved: bool
    success: bool | None = None
    name: str
    message: str
    url: str
    id: int
    Role: str | None = None


class GetUserRoleResponse(BaseModel):
    user_id: int


class DefaultRoleResponse(BaseModel):
    Role: RoleAttributeResponse | None = None
    saved: bool
    success: bool | None = None
    name: str
    message: str
    url: str
    id: int
    errors: str | None = None
