from datetime import datetime

from pydantic import BaseModel

from mmisp.api_schemas.organisations import ShadowAttributeOrganisation


class ShadowAttribute(BaseModel):
    id: int
    old_id: int = 0
    event_id: int
    type: str
    category: str
    uuid: str
    to_ids: bool
    comment: str | None = None
    org_id: int
    timestamp: datetime
    first_seen: str | None = None
    last_seen: str | None = None
    deleted: bool
    proposal_to_delete: bool
    disable_correlation: bool
    value: str
    org_uuid: str
    event_uuid: str
    Org: ShadowAttributeOrganisation
