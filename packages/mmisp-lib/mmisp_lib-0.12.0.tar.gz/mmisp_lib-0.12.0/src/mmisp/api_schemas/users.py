from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel, field_serializer

from mmisp.api_schemas.common import User
from mmisp.api_schemas.organisations import Organisation, OrganisationUsersResponse
from mmisp.api_schemas.roles import Role, RoleUsersResponse


class UserAttributesBody(BaseModel):
    org_id: int | None = None
    authkey: str | None = None
    email: str | None = None
    autoalert: bool | None = None
    gpgkey: str | None = None
    certif_public: str | None = None
    termsaccepted: bool | None = None
    role_id: int | None = None
    change_pw: bool | None = None
    contactalert: bool | None = None
    disabled: bool | None = None
    expiration: datetime | None = None
    force_logout: bool | None = None
    external_auth_required: bool | None = None
    external_auth_key: str | None = None
    notification_daily: bool | None = None
    notification_weekly: bool | None = None
    notification_monthly: bool | None = None
    totp: bool | None = None
    hotp_counter: int | None = None
    name: str | None = None
    nids_sid: int | None = None


class AddUserBody(BaseModel):
    authkey: str
    contactalert: bool
    nids_sid: int
    org_id: int
    email: str
    termsaccepted: bool
    disabled: bool
    notification_daily: bool
    notification_weekly: bool
    notification_monthly: bool
    password: str
    name: str
    """role_id newly added"""
    role_id: int


class AddUserResponseData(BaseModel):
    id: int
    org_id: int
    server_id: int
    email: str
    autoalert: bool
    authkey: str
    invited_by: int
    gpgkey: str | None = None
    certif_public: str | None = None
    nids_sid: int
    termsaccepted: bool
    newsread: int | None = None
    role_id: int
    change_pw: bool
    contactalert: bool
    disabled: bool
    expiration: datetime | None = None
    current_login: datetime
    force_logout: bool
    date_created: datetime
    date_modified: datetime
    sub: str | None = None
    external_auth_required: bool
    external_auth_key: str | None = None
    last_api_access: int
    notification_daily: bool
    notification_weekly: bool
    notification_monthly: bool
    totp: bool | None = None
    hotp_counter: int | None = None
    last_pw_change: int | None = None


class AddUserResponse(BaseModel):
    User: AddUserResponseData


class GetUsersUser(BaseModel):
    id: int
    org_id: int
    server_id: int = 0
    email: str
    autoalert: bool
    auth_key: str | None = None
    invited_by: int
    gpg_key: str | None = None
    certif_public: str | None = None
    nids_sid: int
    termsaccepted: bool
    newsread: int | None = None
    role_id: int
    change_pw: bool
    contactalert: bool
    disabled: bool
    force_logout: bool
    last_api_access: int | None = None
    expiration: datetime | None = None
    current_login: datetime | None = None
    last_login: datetime | None = None
    date_created: datetime | None = None
    date_modified: datetime | None = None
    last_pw_change: int | None = None
    totp: bool | str | None = None
    """detailed information bellow"""
    hotp_counter: int | None = None
    notification_daily: bool | None = None
    notification_weekly: bool | None = None
    notification_monthly: bool | None = None
    external_auth_required: bool | None = None
    external_auth_key: str | None = None
    sub: str | None = None
    """new contents bellow"""  # not in the database, all 3 fields to none now, so no error will be raised
    name: str | None = None
    contact: bool | None = None
    notification: bool | None = None

    @field_serializer("expiration", "current_login", "last_login", "date_created", "date_modified")
    def serialize_timestamp(self: Self, timestamp: datetime | None, _: Any) -> int | None:
        if timestamp is None:
            return None
        return int(timestamp.timestamp())


class GetUsersElement(BaseModel):
    User: GetUsersUser
    Role: RoleUsersResponse
    Organisation: OrganisationUsersResponse
    UserSetting: dict | None = None


class GetAllUsersResponse(BaseModel):
    users: list[GetUsersElement]


class UserWithName(BaseModel):
    user: User
    name: str


class UsersViewMeResponse(BaseModel):
    User: User
    Role: Role
    UserSetting: list = []
    Organisation: Organisation


class ServerUser(BaseModel):
    id: int
    org_id: int
    email: str
    server_id: int
