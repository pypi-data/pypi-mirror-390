from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from mmisp.api_schemas.common import NoneTag, TagAttributesResponse
from mmisp.api_schemas.events import AddEditGetEventGalaxyClusterRelation, GetAllEventsGalaxyClusterGalaxy
from mmisp.api_schemas.galaxies import ExportGalaxyGalaxyElement, RestSearchGalaxyBody
from mmisp.api_schemas.galaxy_common import (
    ShortCommonGalaxy,
    ShortCommonGalaxyCluster,
)
from mmisp.api_schemas.organisations import GetOrganisationElement
from mmisp.lib.distribution import DistributionLevels, GalaxyDistributionLevels


class IndexGalaxyCluster(BaseModel):
    Galaxy: ShortCommonGalaxy
    GalaxyCluster: ShortCommonGalaxyCluster


class ImportGalaxyClusterValueMeta(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: list[str] | None = None
    complexity: str | None = None
    effectiveness: str | None = None
    country: str | None = None
    possible_issues: str | None = None
    colour: str | None = None
    motive: str | None = None
    impact: str | None = None
    refs: list[str] | None = None
    synonyms: list[str] | None = None
    status: str | None = None
    date: str | None = None
    encryption: str | None = None
    extensions: list[str] | None = None
    ransomnotes: list[str] | None = None
    official_refs: list[str] | None = Field(None, validation_alias="official-refs")


class ImportGalaxyClusterValueRelated(BaseModel):
    dest_uuid: UUID = Field(validation_alias="dest-uuid")
    type: str


class ImportGalaxyClusterValue(BaseModel):
    value: str
    uuid: UUID
    related: list[ImportGalaxyClusterValueRelated] | None = None
    description: str = ""
    revoked: bool | None = None
    meta: ImportGalaxyClusterValueMeta | None = None


class ImportGalaxyCluster(BaseModel):
    description: str
    type: str
    version: int
    name: str
    uuid: UUID
    values: list[ImportGalaxyClusterValue]
    authors: list[str]
    source: str
    category: str

    distribution: Literal[3] = 3


class GetGalaxyClusterResponse(BaseModel):
    id: int | None = None
    uuid: str | None = None
    collection_uuid: str
    type: str
    value: str
    tag_name: str
    description: str
    galaxy_id: int
    source: str
    authors: list[str]
    version: int
    distribution: GalaxyDistributionLevels
    sharing_group_id: int | None
    org_id: int
    orgc_id: int
    default: bool
    locked: bool
    extends_uuid: Literal[""] | UUID | None
    extends_version: int | None
    published: bool
    deleted: bool
    RelationshipInbound: list[str] = Field(default_factory=list)
    TargetingClusterRelation: list[str] = Field(default_factory=list)
    GalaxyElement: list[ExportGalaxyGalaxyElement]
    Galaxy: GetAllEventsGalaxyClusterGalaxy | None = None
    GalaxyClusterRelation: list[AddEditGetEventGalaxyClusterRelation] = []
    Org: GetOrganisationElement | None = None
    Orgc: GetOrganisationElement | None = None


class GalaxyClusterResponse(BaseModel):
    GalaxyCluster: GetGalaxyClusterResponse
    Tag: NoneTag | TagAttributesResponse = Field(default_factory=NoneTag)


class AddGalaxyElement(BaseModel):
    key: str
    value: str


class AddUpdateGalaxyElement(BaseModel):
    id: int | None = None
    galaxy_cluster_id: int | None = None
    key: str
    value: str


class AddGalaxyClusterRequest(BaseModel):
    uuid: str | None = None
    value: str
    description: str
    source: str
    authors: list[str]
    org_id: int | None = None
    orgc_id: int | None = None
    distribution: DistributionLevels
    locked: bool = False
    GalaxyElement: list[AddGalaxyElement]


class PutGalaxyClusterRequest(BaseModel):
    id: int | None = None
    uuid: str | None = None
    collection_uuid: UUID | Literal[""] | None = None
    type: str | None = None
    value: str | None = None
    tag_name: str | None = None
    description: str | None = None
    galaxy_id: int | None = None
    source: str | None = None
    authors: list[str] | None = None
    version: int | None = None
    distribution: DistributionLevels
    sharing_group_id: int | None = None
    org_id: int | None = None
    orgc_id: int | None = None
    default: bool | None = None
    locked: bool | None = None
    extends_uuid: str | None = None
    extends_version: str | None = None
    published: bool | None = None
    deleted: bool | None = None
    GalaxyElement: list[AddUpdateGalaxyElement] | None = None


class AddGalaxyClusterResponse(BaseModel):
    pass


class GalaxyClusterRelation(BaseModel):
    id: int
    galaxy_cluster_id: int
    referenced_galaxy_cluster_id: int
    referenced_galaxy_cluster_uuid: str
    referenced_galaxy_cluster_type: str
    galaxy_cluster_uuid: str
    distribution: str
    sharing_group_id: int | None = None
    default: bool


_GalaxyClusterRelation = GalaxyClusterRelation


class SearchGalaxyClusterGalaxyClustersDetails(BaseModel):
    # if minimal is set, only uuid, version and Galaxy is returned

    id: int | None = None
    uuid: str
    collection_uuid: str | None = None
    type: str | None = None
    value: str | None = None
    tag_name: str | None = None
    description: str | None = None
    galaxy_id: int | None = None
    source: str | None = None
    authors: list[str] | None = None
    version: str | int
    distribution: str | int | None = None
    sharing_group_id: int | None = None
    org_id: int | None = None
    orgc_id: int | None = None
    default: bool | None = None
    locked: bool | None = None
    extends_uuid: str | None = None
    extends_version: str | None = None
    published: bool | None = None
    deleted: bool | None = None
    GalaxyElement: Optional[list[ExportGalaxyGalaxyElement]] = None
    Galaxy: RestSearchGalaxyBody
    GalaxyClusterRelation: list[_GalaxyClusterRelation] | None = None
    Org: GetOrganisationElement | None = None
    Orgc: GetOrganisationElement | None = None


class SearchGalaxyClusterGalaxyClusters(BaseModel):
    GalaxyCluster: SearchGalaxyClusterGalaxyClustersDetails


class GalaxyClusterSearchResponse(BaseModel):
    response: list[SearchGalaxyClusterGalaxyClusters]


class GalaxyClusterSearchBody(BaseModel):
    limit: int | None = None
    page: int | None = None
    id: list[int] | None = None
    uuid: list[str] | None = None
    galaxy_id: int | None = None
    galaxy_uuid: str | None = None
    published: bool | None = None
    value: str | None = None
    extends_uuid: str | None = None
    extends_version: str | None = None
    version: int | None = None
    distribution: int | None = None
    org_id: int | None = None
    orgc_id: int | None = None
    tag_name: str | None = None
    custom: bool | None = None  # not sure if bool
    minimal: bool | None = None
