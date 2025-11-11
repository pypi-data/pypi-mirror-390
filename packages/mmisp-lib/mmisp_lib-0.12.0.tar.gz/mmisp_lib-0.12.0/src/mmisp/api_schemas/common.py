from datetime import datetime

from pydantic import BaseModel


class TagAttributesResponse(BaseModel):
    id: int
    name: str
    colour: str
    exportable: bool
    org_id: int | None = None
    user_id: int | None = None
    hide_tag: bool | None = None
    numerical_value: int | None = None
    is_galaxy: bool | None = None
    is_custom_galaxy: bool | None = None
    local_only: bool | None = None


class NoneTag(BaseModel):
    id: int | None = None
    name: str | None = None
    colour: str | None = None
    exportable: bool | None = None
    org_id: int | None = None
    user_id: int | None = None
    hide_tag: bool | None = None
    numerical_value: int | None = None
    is_galaxy: bool | None = None
    is_custom_galaxy: bool | None = None
    local_only: bool | None = None


class User(BaseModel):
    id: int
    org_id: int
    email: str
    autoalert: bool
    invited_by: int
    gpgkey: str | None = None
    certif_public: str | None = None
    termsaccepted: bool
    role_id: int
    change_pw: bool
    contactalert: bool
    disabled: bool
    expiration: datetime | int | None = None
    current_login: datetime
    """time in seconds"""
    last_login: datetime
    """time in seconds"""
    force_logout: bool
    date_created: datetime
    """time in seconds"""
    date_modified: datetime
    """time in seconds"""
    external_auth_required: bool
    external_auth_key: str | None = None
    last_api_access: int
    """time in seconds"""
    notification_daily: bool
    notification_weekly: bool
    notification_monthly: bool
    totp: str | None = None
    hotp_counter: int | None = None
    last_pw_change: int | None = None
    """time in seconds"""
