from sqlalchemy import BigInteger, Boolean, DateTime, Index, Integer, String, Text, VARCHAR, text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(40))
    object_uuid: Mapped[str] = mapped_column(String(40))
    object_type: Mapped[str] = mapped_column(String(80))
    authors: Mapped[str | None] = mapped_column(Text)
    org_uuid: Mapped[str] = mapped_column(String(40))
    orgc_uuid: Mapped[str] = mapped_column(String(40))
    created: Mapped[DateTime] = mapped_column(DateTime)
    modified: Mapped[DateTime] = mapped_column(DateTime)
    distribution: Mapped[int] = mapped_column(Integer)
    sharing_group_id: Mapped[int | None] = mapped_column(Integer)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)
    relationship_type: Mapped[str | None] = mapped_column(String(255))
    related_object_uuid: Mapped[str] = mapped_column(String(40))
    related_object_type: Mapped[str] = mapped_column(String(80))
    __table_args__ = (Index("uuid", "uuid", unique=True),)


class SightingBlocklist(Base):
    __tablename__ = "sighting_blocklists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_uuid: Mapped[str] = mapped_column(String(40))
    created: Mapped[DateTime] = mapped_column(DateTime)
    org_name: Mapped[str] = mapped_column(String(255))
    comment: Mapped[str | None] = mapped_column(Text)


class TemplateElementText(Base):
    __tablename__ = "template_element_texts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    template_element_id: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)


class Inbox(Base):
    __tablename__ = "inbox"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(191))
    type: Mapped[str] = mapped_column(String(191))
    ip: Mapped[str] = mapped_column(String(191))
    user_agent: Mapped[str | None] = mapped_column(Text)
    user_agent_sha256: Mapped[str] = mapped_column(String(64))
    comment: Mapped[str | None] = mapped_column(Text)
    deleted: Mapped[bool] = mapped_column(Boolean)
    timestamp: Mapped[int] = mapped_column(Integer)
    store_as_file: Mapped[bool] = mapped_column(Boolean)
    data: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (Index("uuid", "uuid", unique=True),)


class EventReportTag(Base):
    __tablename__ = "event_report_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_report_id: Mapped[int] = mapped_column(Integer)
    tag_id: Mapped[int] = mapped_column(Integer)
    local: Mapped[bool] = mapped_column(Boolean)
    relationship_type: Mapped[str | None] = mapped_column(String(191))


class CorrelationRule(Base):
    __tablename__ = "correlation_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(191))
    comment: Mapped[str | None] = mapped_column(Text)
    selector_type: Mapped[str] = mapped_column(String(40))
    selector_list: Mapped[str | None] = mapped_column(Text)
    created: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[int] = mapped_column(Integer)


class Regexp(Base):
    __tablename__ = "regexp"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    regexp: Mapped[str] = mapped_column(String(255))
    replacement: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(100))


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created: Mapped[DateTime] = mapped_column(DateTime)
    user_id: Mapped[int] = mapped_column(Integer)
    org_id: Mapped[int] = mapped_column(Integer)
    authkey_id: Mapped[int | None] = mapped_column(Integer)
    ip: Mapped[str | None] = mapped_column(String(16))
    request_type: Mapped[int] = mapped_column(Integer)
    request_id: Mapped[str | None] = mapped_column(String(255))
    action: Mapped[str] = mapped_column(String(20))
    model: Mapped[str] = mapped_column(String(80))
    model_id: Mapped[int] = mapped_column(Integer)
    model_title: Mapped[str | None] = mapped_column(Text)
    event_id: Mapped[int | None] = mapped_column(Integer)
    change: Mapped[str | None] = mapped_column(Text)


class EventReportTemplateVariable(Base):
    __tablename__ = "event_report_template_variables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(191))
    value: Mapped[str | None] = mapped_column(Text)


class FuzzyCorrelateSsdeep(Base):
    __tablename__ = "fuzzy_correlate_ssdeep"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chunk: Mapped[str] = mapped_column(String(12))
    attribute_id: Mapped[int] = mapped_column(Integer)


class Thread(Base):
    __tablename__ = "threads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date_created: Mapped[DateTime] = mapped_column(DateTime)
    date_modified: Mapped[DateTime] = mapped_column(DateTime)
    distribution: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    post_count: Mapped[int] = mapped_column(Integer)
    event_id: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(255))
    org_id: Mapped[int] = mapped_column(Integer)
    sharing_group_id: Mapped[int] = mapped_column(Integer)


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    org_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(191))
    url: Mapped[str] = mapped_column(String(255))
    exposed_to_org: Mapped[bool] = mapped_column(Boolean)
    comment: Mapped[str | None] = mapped_column(Text)


class Opinion(Base):
    __tablename__ = "opinions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(40))
    object_uuid: Mapped[str] = mapped_column(String(40))
    object_type: Mapped[str] = mapped_column(String(80))
    authors: Mapped[str | None] = mapped_column(Text)
    org_uuid: Mapped[str] = mapped_column(String(40))
    orgc_uuid: Mapped[str] = mapped_column(String(40))
    created: Mapped[DateTime] = mapped_column(DateTime)
    modified: Mapped[DateTime] = mapped_column(DateTime)
    distribution: Mapped[int] = mapped_column(Integer)
    sharing_group_id: Mapped[int | None] = mapped_column(Integer)
    locked: Mapped[bool] = mapped_column(Boolean)
    opinion: Mapped[int | None] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (Index("uuid", "uuid", unique=True),)


class Bruteforce(Base):
    __tablename__ = "bruteforces"

    ip: Mapped[str] = mapped_column(String(255), primary_key=True)
    username: Mapped[str] = mapped_column(String(255), primary_key=True)
    expire: Mapped[DateTime] = mapped_column(DateTime)


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(40))
    object_uuid: Mapped[str] = mapped_column(String(40))
    object_type: Mapped[str] = mapped_column(String(80))
    authors: Mapped[str | None] = mapped_column(Text)
    org_uuid: Mapped[str] = mapped_column(String(40))
    orgc_uuid: Mapped[str] = mapped_column(String(40))
    created: Mapped[DateTime] = mapped_column(DateTime)
    modified: Mapped[DateTime] = mapped_column(DateTime)
    distribution: Mapped[int] = mapped_column(Integer)
    sharing_group_id: Mapped[int | None] = mapped_column(Integer)
    locked: Mapped[bool] = mapped_column(Boolean)
    note: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(16))
    __table_args__ = (Index("uuid", "uuid", unique=True),)


class TagCollection(Base):
    __tablename__ = "tag_collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str | None] = mapped_column(String(40))
    user_id: Mapped[int] = mapped_column(Integer)
    org_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    all_orgs: Mapped[bool] = mapped_column(Boolean)
    __table_args__ = (Index("uuid", "uuid", unique=True),)


class Cerebrate(Base):
    __tablename__ = "cerebrates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(191))
    url: Mapped[str] = mapped_column(String(255))
    authkey: Mapped[str] = mapped_column(String(255))
    open: Mapped[bool | None] = mapped_column(Boolean)
    org_id: Mapped[int] = mapped_column(Integer)
    pull_orgs: Mapped[bool | None] = mapped_column(Boolean)
    pull_sharing_groups: Mapped[bool | None] = mapped_column(Boolean)
    self_signed: Mapped[bool | None] = mapped_column(Boolean)
    cert_file: Mapped[str | None] = mapped_column(String(255))
    client_cert_file: Mapped[str | None] = mapped_column(String(255))
    internal: Mapped[bool] = mapped_column(Boolean)
    skip_proxy: Mapped[bool] = mapped_column(Boolean)
    description: Mapped[str | None] = mapped_column(Text)


class CollectionElement(Base):
    __tablename__ = "collection_elements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(40))
    element_uuid: Mapped[str] = mapped_column(String(40))
    element_type: Mapped[str] = mapped_column(String(80))
    collection_id: Mapped[int] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (
        Index("unique_element", "element_uuid", "collection_id", unique=True),
        Index("uuid", "uuid", unique=True),
    )


class TemplateElementAttribute(Base):
    __tablename__ = "template_element_attributes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_element_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    to_ids: Mapped[bool] = mapped_column(Boolean)
    category: Mapped[str] = mapped_column(String(255))
    complex: Mapped[bool] = mapped_column(Boolean)
    type: Mapped[str] = mapped_column(String(255))
    mandatory: Mapped[bool] = mapped_column(Boolean)
    batch: Mapped[bool] = mapped_column(Boolean)


class DecayingModelMapping(Base):
    __tablename__ = "decaying_model_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attribute_type: Mapped[str] = mapped_column(String(255))
    model_id: Mapped[int] = mapped_column(Integer)


class Allowedlist(Base):
    __tablename__ = "allowedlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)


class ShadowAttributeCorrelation(Base):
    __tablename__ = "shadow_attribute_correlations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(Integer)
    value: Mapped[str] = mapped_column(Text)
    distribution: Mapped[int] = mapped_column(Integer)
    a_distribution: Mapped[int] = mapped_column(Integer)
    sharing_group_id: Mapped[int | None] = mapped_column(Integer)
    a_sharing_group_id: Mapped[int | None] = mapped_column(Integer)
    attribute_id: Mapped[int] = mapped_column(Integer)
    shadow_attribute_id_1: Mapped[int] = mapped_column("1_shadow_attribute_id", Integer)
    event_id: Mapped[int] = mapped_column(Integer)
    event_id_1: Mapped[int] = mapped_column("1_event_id", Integer)
    info: Mapped[str] = mapped_column(Text)


class NoAclCorrelation(Base):
    __tablename__ = "no_acl_correlations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attribute_id: Mapped[int] = mapped_column(Integer)
    attribute_id_1: Mapped[int] = mapped_column("1_attribute_id", Integer)
    event_id: Mapped[int] = mapped_column(Integer)
    event_id_1: Mapped[int] = mapped_column("1_event_id", Integer)
    value_id: Mapped[int] = mapped_column(Integer)
    __table_args__ = (Index("unique_correlation", "attribute_id", "1_attribute_id", "value_id", unique=True),)


__table_args__ = (Index("unique_correlation", "attribute_id", "1_attribute_id", "value_id", unique=True),)


class RestClientHistory(Base):
    __tablename__ = "rest_client_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    headers: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    http_method: Mapped[str | None] = mapped_column(String(255))
    timestamp: Mapped[int] = mapped_column(Integer)
    use_full_path: Mapped[bool | None] = mapped_column(Boolean)
    show_result: Mapped[bool | None] = mapped_column(Boolean)
    skip_ssl: Mapped[bool | None] = mapped_column(Boolean)
    outcome: Mapped[int] = mapped_column(Integer)
    bookmark: Mapped[bool] = mapped_column(Boolean)
    bookmark_name: Mapped[str | None] = mapped_column(String(255))


class SharingGroupBlueprint(Base):
    __tablename__ = "sharing_group_blueprints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(191))
    timestamp: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    org_id: Mapped[int] = mapped_column(Integer)
    sharing_group_id: Mapped[int | None] = mapped_column(Integer)
    rules: Mapped[str | None] = mapped_column(Text)


class TagCollectionTag(Base):
    __tablename__ = "tag_collection_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag_collection_id: Mapped[int] = mapped_column(Integer)
    tag_id: Mapped[int] = mapped_column(Integer)


class UserLoginProfile(Base):
    __tablename__ = "user_login_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime)
    user_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[str | None] = mapped_column(String(191))
    ip: Mapped[str | None] = mapped_column(String(191))
    user_agent: Mapped[str | None] = mapped_column(String(191))
    accept_lang: Mapped[str | None] = mapped_column(String(191))
    geoip: Mapped[str | None] = mapped_column(String(191))
    ua_platform: Mapped[str | None] = mapped_column(String(191))
    ua_browser: Mapped[str | None] = mapped_column(String(191))
    ua_pattern: Mapped[str | None] = mapped_column(String(191))
    hash: Mapped[str] = mapped_column(VARCHAR(32))

    __table_args__ = (Index("hash", "hash", unique=True),)


class Correlation(Base):
    __tablename__ = "correlations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    event_id_1: Mapped[int] = mapped_column("1_event_id", Integer)
    attribute_id_1: Mapped[int] = mapped_column("1_attribute_id", Integer)
    event_id: Mapped[int] = mapped_column(Integer)
    attribute_id: Mapped[int] = mapped_column(Integer)
    org_id: Mapped[int] = mapped_column(Integer)
    distribution: Mapped[int] = mapped_column(Integer)
    a_distribution: Mapped[int] = mapped_column(Integer)
    sharing_group_id: Mapped[int] = mapped_column(Integer)
    a_sharing_group_id: Mapped[int] = mapped_column(Integer)


class CryptographicKey(Base):
    __tablename__ = "cryptographic_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(40))
    type: Mapped[str] = mapped_column(String(40))
    timestamp: Mapped[int] = mapped_column(Integer)
    parent_id: Mapped[int] = mapped_column(Integer)
    parent_type: Mapped[str] = mapped_column(String(40))
    key_data: Mapped[str | None] = mapped_column(Text)
    revoked: Mapped[bool] = mapped_column(Boolean)
    fingerprint: Mapped[str] = mapped_column(String(255))


class DecayingModel(Base):
    __tablename__ = "decaying_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str | None] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(255))
    parameters: Mapped[str | None] = mapped_column(Text)
    attribute_types: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    org_id: Mapped[int | None] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean)
    all_orgs: Mapped[bool] = mapped_column(Boolean)
    ref: Mapped[str | None] = mapped_column(Text)
    formula: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(255))
    default: Mapped[bool] = mapped_column(Boolean)


class SightingdbOrg(Base):
    __tablename__ = "sightingdb_orgs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sightingdb_id: Mapped[int] = mapped_column(Integer)
    org_id: Mapped[int] = mapped_column(Integer)


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(nullable=False)
    date_created: Mapped[int] = mapped_column(nullable=False)


class EventGraph(Base):
    __tablename__ = "event_graph"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)
    org_id: Mapped[int] = mapped_column(nullable=False)
    timestamp: Mapped[int] = mapped_column(nullable=False)
    network_name: Mapped[str | None] = mapped_column(String(255))
    network_json: Mapped[str] = mapped_column(Text)
    preview_img: Mapped[str | None] = mapped_column(Text)


class SystemSetting(Base):
    __tablename__ = "system_settings"

    setting: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[str] = mapped_column(Text)


class EventDelegation(Base):
    __tablename__ = "event_delegations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(Integer)
    requester_org_id: Mapped[int] = mapped_column(Integer)
    event_id: Mapped[int] = mapped_column(Integer)
    message: Mapped[str | None] = mapped_column(Text)
    distribution: Mapped[int] = mapped_column(Integer)
    sharing_group_id: Mapped[int | None] = mapped_column(Integer)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(100))
    timer: Mapped[int] = mapped_column(Integer)
    scheduled_time: Mapped[str] = mapped_column(String(8))
    process_id: Mapped[str | None] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(String(255))
    next_execution_time: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(String(255))


class TemplateTag(Base):
    __tablename__ = "template_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_id: Mapped[int] = mapped_column(Integer)
    tag_id: Mapped[int] = mapped_column(Integer)


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[int] = mapped_column(Integer)


class FavouriteTag(Base):
    __tablename__ = "favourite_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)


class ObjectReference(Base):
    __tablename__ = "object_references"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str | None] = mapped_column(String(40))
    timestamp: Mapped[int] = mapped_column(Integer)
    object_id: Mapped[int] = mapped_column(Integer)
    event_id: Mapped[int] = mapped_column(Integer)
    source_uuid: Mapped[str | None] = mapped_column(String(40))
    referenced_uuid: Mapped[str | None] = mapped_column(String(40))
    referenced_id: Mapped[int] = mapped_column(Integer)
    referenced_type: Mapped[int] = mapped_column(Integer)
    relationship_type: Mapped[str | None] = mapped_column(String(255))
    comment: Mapped[str] = mapped_column(Text)
    deleted: Mapped[bool] = mapped_column(Boolean)
    __table_args__ = (Index("uuid", "uuid", unique=True),)


__table_args__ = (Index("uuid", "uuid", unique=True),)


class TaxiiServer(Base):
    __tablename__ = "taxii_servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(191))
    owner: Mapped[str] = mapped_column(String(191))
    baseurl: Mapped[str] = mapped_column(String(191))
    api_root: Mapped[str] = mapped_column(String(191))
    description: Mapped[str | None] = mapped_column(Text)
    filters: Mapped[str | None] = mapped_column(Text)
    api_key: Mapped[str] = mapped_column(String(255))
    collection: Mapped[str | None] = mapped_column(String(40))
    skip_proxy: Mapped[bool] = mapped_column(Boolean)


class ObjectRelationship(Base):
    __tablename__ = "object_relationships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[int] = mapped_column(Integer)
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    format: Mapped[str] = mapped_column(Text)
    highlighted: Mapped[bool | None] = mapped_column(Boolean)


class AccessLog(Base):
    __tablename__ = "access_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created: Mapped[DateTime] = mapped_column(DateTime)
    user_id: Mapped[int] = mapped_column(Integer)
    org_id: Mapped[int] = mapped_column(Integer)
    authkey_id: Mapped[int | None] = mapped_column(Integer)
    ip: Mapped[str | None] = mapped_column(String(64))
    request_method: Mapped[int] = mapped_column(Integer)
    user_agent: Mapped[str | None] = mapped_column(String(255))
    request_id: Mapped[str | None] = mapped_column(String(255))
    controller: Mapped[str] = mapped_column(String(20))
    action: Mapped[str] = mapped_column(String(191))
    url: Mapped[str] = mapped_column(String(255))
    request: Mapped[str | None] = mapped_column(String(1024))
    response_code: Mapped[int] = mapped_column(Integer)
    memory_usage: Mapped[int] = mapped_column(Integer)
    duration: Mapped[int] = mapped_column(Integer)
    query_count: Mapped[int] = mapped_column(Integer)
    query_log: Mapped[str | None] = mapped_column(String(2048))


class Dashboard(Base):
    __tablename__ = "dashboards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(191))
    description: Mapped[str | None] = mapped_column(Text)
    default: Mapped[bool] = mapped_column(Boolean)
    selectable: Mapped[bool] = mapped_column(Boolean)
    user_id: Mapped[int] = mapped_column(Integer)
    restrict_to_org_id: Mapped[int] = mapped_column(Integer)
    restrict_to_role_id: Mapped[int] = mapped_column(Integer)
    restrict_to_permission_flag: Mapped[str] = mapped_column(String(191))
    value: Mapped[str | None] = mapped_column(Text)
    timestamp: Mapped[int] = mapped_column(Integer)

    __table_args__ = (Index("uuid", "uuid", unique=True),)


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    org: Mapped[str] = mapped_column(String(255))
    share: Mapped[bool] = mapped_column(Boolean)


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(40))
    org_id: Mapped[int] = mapped_column(Integer)
    orgc_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    created: Mapped[DateTime] = mapped_column(DateTime)
    modified: Mapped[DateTime] = mapped_column(DateTime)
    distribution: Mapped[int] = mapped_column(Integer)
    sharing_group_id: Mapped[int | None] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(191))
    type: Mapped[str] = mapped_column(String(80))
    description: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (Index("uuid", "uuid", unique=True),)


class SightingDb(Base):
    __tablename__ = "sightingdbs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    owner: Mapped[str | None] = mapped_column(String(255))
    host: Mapped[str | None] = mapped_column(String(255))
    port: Mapped[int | None] = mapped_column(Integer)
    timestamp: Mapped[int] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean)
    skip_proxy: Mapped[bool] = mapped_column(Boolean)
    ssl_skip_verification: Mapped[bool] = mapped_column(Boolean)
    namespace: Mapped[str | None] = mapped_column(String(255))


class EventLock(Base):
    __tablename__ = "event_locks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[int] = mapped_column(Integer)


class AttachmentScan(Base):
    __tablename__ = "attachment_scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(40))
    attribute_id: Mapped[int] = mapped_column(Integer)
    infected: Mapped[bool] = mapped_column(Boolean)
    malware_name: Mapped[str | None] = mapped_column(String(191))
    timestamp: Mapped[int] = mapped_column(Integer)


Index("index", AttachmentScan.type, AttachmentScan.attribute_id)


class TemplateElementFile(Base):
    __tablename__ = "template_element_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_element_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(255))
    malware: Mapped[bool] = mapped_column(Boolean)
    mandatory: Mapped[bool] = mapped_column(Boolean)
    batch: Mapped[bool] = mapped_column(Boolean)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    worker: Mapped[str] = mapped_column(String(32))
    job_type: Mapped[str] = mapped_column(String(32))
    job_input: Mapped[str] = mapped_column(Text)
    status: Mapped[bool] = mapped_column(Boolean)
    retries: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(Text)
    progress: Mapped[int] = mapped_column(Integer)
    org_id: Mapped[int] = mapped_column(Integer)
    process_id: Mapped[str | None] = mapped_column(String(36))
    date_created: Mapped[DateTime] = mapped_column(DateTime)
    date_modified: Mapped[DateTime] = mapped_column(DateTime)


class CakeSession(Base):
    __tablename__ = "cake_sessions"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    data: Mapped[str] = mapped_column(Text)
    expires: Mapped[int] = mapped_column(Integer)


class AnalystDataBlocklist(Base):
    __tablename__ = "analyst_data_blocklists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analyst_data_uuid: Mapped[str] = mapped_column(String(40))
    created: Mapped[DateTime] = mapped_column(DateTime)
    analyst_data_info: Mapped[str] = mapped_column(Text)
    comment: Mapped[str | None] = mapped_column(Text)
    analyst_data_orgc: Mapped[str] = mapped_column(String(255))


class TemplateElement(Base):
    __tablename__ = "template_elements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_id: Mapped[int] = mapped_column(Integer)
    position: Mapped[int] = mapped_column(Integer)
    element_definition: Mapped[str] = mapped_column(String(255))


class AttrValueCounts(Base):
    __tablename__ = "attr_value_counts"

    value: Mapped[str] = mapped_column(String(64), primary_key=True)
    cnt_v1: Mapped[int] = mapped_column(Integer)
    cnt_v2: Mapped[int] = mapped_column(Integer)


class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(100))
    timer: Mapped[int] = mapped_column(Integer)
    last_job_id: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(255))
    next_execution_time: Mapped[int] = mapped_column(Integer)
    message: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(Integer)
    action: Mapped[str] = mapped_column(String(40))
    params: Mapped[str | None] = mapped_column(String(255))
    enabled: Mapped[bool | None] = mapped_column(Boolean)
    last_run_at: Mapped[int | None] = mapped_column(Integer)
