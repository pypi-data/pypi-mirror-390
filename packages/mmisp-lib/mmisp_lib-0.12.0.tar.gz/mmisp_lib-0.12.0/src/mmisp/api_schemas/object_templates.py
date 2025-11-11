from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from mmisp.lib.attributes import (
    AttributeCategories,
    literal_valid_attribute_types,
)


class CommonObjectTemplateElement(BaseModel):
    ui_priority: int = Field(..., alias="ui-priority")
    description: str
    categories: list[AttributeCategories] = []
    sane_default: list[str] = []
    values_list: list[str] = []
    disable_correlation: bool | None = None
    multiple: bool = False


class ImportObjectTemplateElement(CommonObjectTemplateElement):
    misp_attribute: literal_valid_attribute_types = Field(..., alias="misp-attribute")
    recommended: bool = False
    to_ids: bool = True


class ObjectTemplatesRequirements(BaseModel):
    requiredOneOf: list[str] | None = None
    required: list[str] | None = None


class ImportObjectTemplate(BaseModel):
    version: int
    description: str
    meta_category: str = Field(..., alias="meta-category")
    uuid: UUID
    name: str


class ImportObjectTemplateFile(ImportObjectTemplate, ObjectTemplatesRequirements):
    attributes: dict[str, ImportObjectTemplateElement]


class ObjectTemplate(ImportObjectTemplate):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    user_id: int
    org_id: int
    requirements: ObjectTemplatesRequirements
    fixed: bool
    active: bool


class ObjectTemplateElement(CommonObjectTemplateElement):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    object_template_id: int
    object_relation: str
    type: str  # AttributeType?


class RespObjectTemplateView(BaseModel):
    ObjectTemplate: ObjectTemplate
    ObjectTemplateElement: list[ObjectTemplateElement]


class RespItemObjectTemplateIndex(BaseModel):
    ObjectTemplate: ObjectTemplate
