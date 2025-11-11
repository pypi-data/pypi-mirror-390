from datetime import datetime
from typing import Literal, Self
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from mmisp.lib.distribution import GalaxyDistributionLevels


class ShortCommonGalaxy(BaseModel):
    id: int
    uuid: UUID
    name: str
    type: str
    description: str
    version: str | int
    namespace: str
    kill_chain_order: str | None = None
    default: bool


class ShortCommonGalaxyCluster(BaseModel):
    id: int
    uuid: UUID
    collection_uuid: UUID | Literal[""]
    type: str
    value: str
    tag_name: str
    description: str
    galaxy_id: int
    source: str
    authors: list[str]
    version: str | int
    distribution: GalaxyDistributionLevels | None = None
    sharing_group_id: int | None = None
    org_id: int
    orgc_id: int
    default: bool | None = None
    locked: bool | None = None
    extends_uuid: UUID | Literal[""] | None = None
    extends_version: str | int | None = None
    published: bool | None = None
    deleted: bool | None = None


class CommonGalaxy(BaseModel):
    id: int
    uuid: UUID
    name: str
    type: str
    description: str
    version: str | int
    icon: str
    namespace: str
    enabled: bool
    local_only: bool
    kill_chain_order: str | None = None
    created: Literal["0000-00-00 00:00:00"] | datetime
    modified: Literal["0000-00-00 00:00:00"] | datetime
    org_id: int
    orgc_id: int
    default: bool
    distribution: GalaxyDistributionLevels

    @field_serializer("created", "modified")
    def serialize_timestamp(self: Self, value: datetime | Literal["0000-00-00 00:00:00"]) -> str:
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value


class GalaxyClusterMeta(BaseModel):
    external_id: int | None = None
    refs: list[str] | None = None
    kill_chain: str | None = None


class CommonGalaxyCluster(BaseModel):
    id: int
    uuid: UUID
    collection_uuid: Literal[""] | UUID
    type: str
    value: str
    tag_name: str
    description: str
    galaxy_id: int
    source: str
    authors: list[str]
    version: str | int
    distribution: GalaxyDistributionLevels | None = None
    sharing_group_id: int | None = None
    org_id: int
    orgc_id: int
    default: bool | None = None
    locked: bool | None = None
    extends_uuid: Literal[""] | UUID | None = None
    extends_version: str | int | None = None
    published: bool | None = None
    deleted: bool | None = None
    meta: GalaxyClusterMeta | None = None
    tag_id: int
    local: bool | None = None
    relationship_type: bool | str = ""

    TargetingClusterRelation: list = Field(default_factory=list)


class GetAllSearchGalaxiesAttributes(CommonGalaxy):
    pass
