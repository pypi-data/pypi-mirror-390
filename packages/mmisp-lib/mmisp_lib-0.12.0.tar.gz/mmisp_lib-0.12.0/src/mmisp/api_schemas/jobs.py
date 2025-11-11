from pydantic import BaseModel, ConfigDict


class FreeTextProcessID(BaseModel):
    id: str


class FreeTextImportWorkerData(BaseModel):
    data: str


class FreeTextImportWorkerUser(BaseModel):
    user_id: int


class FreeTextImportWorkerBody(BaseModel):
    user: FreeTextImportWorkerUser
    data: FreeTextImportWorkerData
    model_config = ConfigDict(from_attributes=True)


class AddAttributeViaFreeTextImportEventResponse(BaseModel):
    event_id: str
    value: str
    original_value: str
    to_ids: str
    type: str
    category: str
    distribution: str
    model_config = ConfigDict(from_attributes=True)


class AddAttributeViaFreeTextImportEventBody(BaseModel):
    value: str
    returnMetaAttributes: bool
    model_config = ConfigDict(from_attributes=True)


class AttributeType(BaseModel):
    types: list[str]
    default_type: str
    value: str


class ProcessFreeTextResponse(BaseModel):
    attributes: list[AttributeType]
