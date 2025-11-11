from typing import Any, Self, Type

from pydantic import BaseModel, Field, Json, field_serializer, field_validator

from mmisp.api_schemas.organisations import BaseOrganisation


class NOT_Filter(BaseModel):
    NOT: list


class OR_NOT_Filter(BaseModel):
    OR: list
    NOT: list


class PullRulesFilter(BaseModel):
    tags: OR_NOT_Filter
    orgs: OR_NOT_Filter
    type_attributes: NOT_Filter
    type_objects: NOT_Filter
    url_params: str


class PushRulesFilter(BaseModel):
    tags: OR_NOT_Filter
    orgs: OR_NOT_Filter


default_pull_rules = PullRulesFilter(
    tags=OR_NOT_Filter(OR=[], NOT=[]),
    orgs=OR_NOT_Filter(OR=[], NOT=[]),
    type_attributes=NOT_Filter(NOT=[]),
    type_objects=NOT_Filter(NOT=[]),
    url_params="",
)
default_push_rules = PushRulesFilter(
    tags=OR_NOT_Filter(OR=[], NOT=[]),
    orgs=OR_NOT_Filter(OR=[], NOT=[]),
)


class RulesWithValidator(BaseModel):
    pull_rules: Json[PullRulesFilter] | PullRulesFilter = default_pull_rules
    push_rules: Json[PushRulesFilter] | PushRulesFilter = default_push_rules

    @field_validator("pull_rules", mode="before")
    @classmethod
    def set_default_pull(cls: Type[Self], value: Any) -> Any:
        if value is None:
            return default_pull_rules
        if value == "":
            return default_pull_rules
        return value

    @field_validator("push_rules", mode="before")
    @classmethod
    def set_default_push(cls: Type[Self], value: Any) -> Any:
        if value is None:
            return default_push_rules
        if value == "":
            return default_push_rules
        return value

    @field_serializer("push_rules", "pull_rules")
    def serialize_rules(self: Self, val: PullRulesFilter | PushRulesFilter, _info: Any) -> str:
        return val.model_dump_json()


class AddServer(RulesWithValidator):
    url: str
    name: str
    remote_org_id: int
    authkey: str
    org_id: int | None = None
    priority: int = 5
    internal: bool = False
    push: bool = False
    pull: bool = False
    push_galaxy_clusters: bool = False
    caching_enabled: bool = False
    unpublish_event: bool = False
    publish_without_email: bool = False
    self_signed: bool = False
    skip_proxy: bool = False


class EditServer(RulesWithValidator):
    name: str
    url: str
    priority: int
    authkey: str
    remote_org_id: int
    internal: bool
    push: bool
    pull: bool
    push_galaxy_clusters: bool
    caching_enabled: bool
    unpublish_event: bool
    publish_without_email: bool
    self_signed: bool
    skip_proxy: bool
    last_pushed_id: int | None = None


class ServerResponseBase(BaseModel):
    id: int
    name: str
    url: str
    #    authkey: str
    org_id: int | None = None
    push: bool
    pull: bool
    cert_file: str | None = None
    client_cert_file: str | None = None
    lastpulledid: int | None = Field(None, validation_alias="last_pulled_id")
    lastpushedid: int | None = Field(None, validation_alias="last_pushed_id")
    organization: str | None = None
    pull_analyst_data: bool
    pull_rules: str
    push_analyst_data: bool
    push_rules: str
    remove_missing_tags: bool
    push_sightings: bool | None = None
    push_galaxy_clusters: bool | None = None
    pull_galaxy_clusters: bool | None = None
    remote_org_id: int
    publish_without_email: bool | None = None
    unpublish_event: bool | None = None
    self_signed: bool
    internal: bool | None = None
    skip_proxy: bool | None = None
    caching_enabled: bool | None = None
    priority: int | None = None


class ServerResponse(ServerResponseBase):
    cache_timestamp: bool = False


class AddServerServer(ServerResponseBase):
    authkey: str


class AddServerResponse(BaseModel):
    Server: AddServerServer


class RemoveServer(BaseModel):
    id: int
    sharing_group_id: int
    server_id: int
    all_orgs: bool


class GetRemoteServer(BaseModel):
    Server: ServerResponse
    Organisation: BaseOrganisation
    RemoteOrg: BaseOrganisation
    User: list


class ServersGetVersion(BaseModel):
    pass
