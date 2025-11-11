import uuid as libuuid
from contextlib import AsyncExitStack
from datetime import date, datetime
from typing import Self

import pytest
import pytest_asyncio
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import mmisp.db.all_models  # noqa
import mmisp.lib.standard_roles as standard_roles
import mmisp.lib.standard_threat_levels as standard_threat_levels
from mmisp.db.database import DatabaseSessionManager
from mmisp.db.models.attribute import Attribute
from mmisp.db.models.auth_key import AuthKey
from mmisp.db.models.galaxy import Galaxy
from mmisp.db.models.galaxy_cluster import GalaxyCluster, GalaxyElement
from mmisp.db.models.sharing_group import SharingGroupOrg
from mmisp.db.models.tag import Tag
from mmisp.lib.distribution import AttributeDistributionLevels, DistributionLevels, EventDistributionLevels
from mmisp.lib.galaxies import galaxy_tag_name
from mmisp.util.crypto import hash_secret
from mmisp.util.uuid import uuid

from ..db.models.blocklist import GalaxyClusterBlocklist
from ..db.models.correlation import CorrelationExclusions, CorrelationValue, DefaultCorrelation, OverCorrelatingValue
from ..db.models.event import Event, EventTag
from ..db.models.object import Object
from ..db.models.post import Post
from ..db.models.sighting import Sighting
from ..db.models.threat_level import ThreatLevel
from .generators.model_generators.attribute_generator import generate_attribute
from .generators.model_generators.correlation_exclusions_generator import generate_correlation_exclusions
from .generators.model_generators.correlation_value_generator import (
    generate_correlation_value,
)
from .generators.model_generators.default_correlation_generator import generate_default_correlation
from .generators.model_generators.event_blocklist_generator import generate_event_blocklist
from .generators.model_generators.galaxy_cluster_blocklist_generator import generate_galaxy_cluster_blocklist
from .generators.model_generators.object_generator import generate_object
from .generators.model_generators.org_blocklist_generator import generate_org_blocklist
from .generators.model_generators.organisation_generator import generate_organisation
from .generators.model_generators.over_correlating_value_generator import (
    generate_over_correlating_value,
)
from .generators.model_generators.post_generator import generate_post
from .generators.model_generators.role_generator import (
    generate_org_admin_role,
    generate_read_only_role,
)
from .generators.model_generators.server_generator import generate_server
from .generators.model_generators.shadow_attribute_generator import generate_shadow_attribute
from .generators.model_generators.sharing_group_generator import generate_sharing_group
from .generators.model_generators.sighting_generator import generate_sighting
from .generators.model_generators.tag_generator import generate_tag
from .generators.model_generators.threat_level_generator import generate_threat_level
from .generators.model_generators.user_generator import generate_user
from .generators.model_generators.user_setting_generator import generate_user_name


class DBManager:
    def __init__(self: Self, db: AsyncSession, obj) -> None:  # noqa
        self.db = db
        self.obj = obj

    async def __aenter__(self: Self):  # noqa
        self.db.add(self.obj)
        await self.db.flush()
        return self.obj

    async def __aexit__(self: Self, exc_type, exc, tb):  # noqa
        await self.db.delete(self.obj)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def db_connection():
    sm = DatabaseSessionManager()
    sm.init()
    await sm.create_all()
    yield sm


@pytest_asyncio.fixture
async def db(db_connection):
    async with db_connection.session() as session:
        yield session


@pytest_asyncio.fixture
async def site_admin_role(db):
    role = standard_roles.site_admin_role()
    role.id = None
    db.add(role)
    await db.commit()
    await db.refresh(role)
    yield role
    await db.delete(role)
    await db.commit()


@pytest_asyncio.fixture
async def threat_levels(db):
    threat_levels = []
    for tl in standard_threat_levels.get_standard_threat_level():
        threat_levels.append(tl)
        db.add(tl)
    await db.commit()

    yield threat_levels

    for tl in threat_levels:
        await db.delete(tl)
    await db.commit()


@pytest_asyncio.fixture
async def user_role(db):
    role = generate_read_only_role()
    db.add(role)
    await db.commit()
    yield role
    await db.delete(role)
    await db.commit()


@pytest_asyncio.fixture
async def org_admin_role(db):
    role = generate_org_admin_role()
    db.add(role)
    await db.commit()
    yield role
    await db.delete(role)
    await db.commit()


@pytest_asyncio.fixture
async def instance_owner_org(db):
    instance_owner_org = generate_organisation()
    db.add(instance_owner_org)
    await db.commit()
    await db.refresh(instance_owner_org)
    yield instance_owner_org
    await db.delete(instance_owner_org)
    await db.commit()


@pytest_asyncio.fixture
async def instance_org_two(db):
    org = generate_organisation()
    db.add(org)
    await db.commit()
    await db.refresh(org)
    yield org
    await db.delete(org)
    await db.commit()


@pytest_asyncio.fixture
async def instance_two_owner_org(db):
    org = generate_organisation()
    org.local = False
    db.add(org)
    await db.commit()
    await db.refresh(org)
    yield org
    await db.delete(org)
    await db.commit()


@pytest_asyncio.fixture
async def site_admin_user(db, site_admin_role, instance_owner_org):
    assert instance_owner_org.local

    user = generate_user()
    user.org_id = instance_owner_org.id
    user.server_id = 0
    user.role_id = site_admin_role.id

    db.add(user)
    await db.commit()
    await db.refresh(user)

    user_setting = generate_user_name()
    user_setting.user_id = user.id

    db.add(user_setting)
    await db.commit()

    yield user
    await db.delete(user_setting)
    await db.commit()
    await db.delete(user)
    await db.commit()


@pytest_asyncio.fixture
async def view_only_user(db, user_role, instance_owner_org):
    user = generate_user()
    user.org_id = instance_owner_org.id
    user.server_id = 0
    user.role_id = user_role.id

    db.add(user)
    await db.commit()
    await db.refresh(user)

    user_setting = generate_user_name()
    user_setting.user_id = user.id

    db.add(user_setting)
    await db.commit()

    yield user
    await db.delete(user_setting)
    await db.commit()
    await db.delete(user)
    await db.commit()


@pytest_asyncio.fixture
async def instance_owner_org_admin_user(db, instance_owner_org, org_admin_role):
    user = generate_user()
    user.org_id = instance_owner_org.id
    user.server_id = 0
    user.role_id = org_admin_role.id

    db.add(user)
    await db.commit()
    await db.refresh(user)

    user_setting = generate_user_name()
    user_setting.user_id = user.id

    db.add(user_setting)
    await db.commit()

    yield user
    await db.delete(user_setting)
    await db.commit()
    await db.delete(user)
    await db.commit()


@pytest_asyncio.fixture
async def instance_two_server(db, instance_two_owner_org):
    server = generate_server()
    server.name = "Instance Two Server"
    server.org_id = instance_two_owner_org.id
    server.url = "http://instance-two.mmisp.service"

    db.add(server)
    await db.commit()
    yield server
    await db.delete(server)
    await db.commit()


@pytest_asyncio.fixture
async def instance_org_two_admin_user(db, instance_org_two, org_admin_role):
    user = generate_user()
    user.org_id = instance_org_two.id
    user.server_id = 0
    user.role_id = org_admin_role.id

    db.add(user)
    await db.commit()
    await db.refresh(user)

    user_setting = generate_user_name()
    user_setting.user_id = user.id

    db.add(user_setting)
    await db.commit()

    yield user
    await db.delete(user_setting)
    await db.commit()
    await db.delete(user)
    await db.commit()


@pytest_asyncio.fixture
async def instance_two_owner_org_admin_user(db, instance_two_owner_org, instance_two_server, org_admin_role):
    user = generate_user()
    user.org_id = instance_two_owner_org.id
    user.server_id = instance_two_server.id
    user.role_id = org_admin_role.id

    db.add(user)
    await db.commit()
    await db.refresh(user)

    user_setting = generate_user_name()
    user_setting.user_id = user.id

    db.add(user_setting)
    await db.commit()

    yield user
    await db.delete(user_setting)
    await db.commit()
    await db.delete(user)
    await db.commit()


@pytest_asyncio.fixture
async def organisation(db):
    organisation = generate_organisation()

    db.add(organisation)
    await db.commit()
    await db.refresh(organisation)

    yield organisation

    await db.delete(organisation)
    await db.commit()


@pytest_asyncio.fixture
async def event(db, organisation, site_admin_user):
    org_id = organisation.id
    event = Event(
        org_id=org_id,
        orgc_id=org_id,
        user_id=site_admin_user.id,
        uuid=libuuid.uuid4(),
        sharing_group_id=0,
        threat_level_id=1,
        info="test event",
        date=date(year=2024, month=2, day=13),
        analysis=1,
        distribution=EventDistributionLevels.ALL_COMMUNITIES,
    )
    async with DBManager(db, event) as obj:
        await db.commit()
        yield obj
    await db.commit()


@pytest_asyncio.fixture
async def event_unpublished_sharing_group(db, organisation, site_admin_user, sharing_group):
    event = Event(
        org_id=organisation.id,
        orgc_id=organisation.id,
        user_id=site_admin_user.id,
        uuid=libuuid.uuid4(),
        sharing_group_id=sharing_group.id,
        threat_level_id=1,
        info="event_unpublished_sharing_group",
        date=date(year=2024, month=2, day=13),
        analysis=1,
        distribution=EventDistributionLevels.SHARING_GROUP,
        published=False,
    )
    async with DBManager(db, event) as obj:
        await db.commit()
        yield obj
    await db.commit()


@pytest_asyncio.fixture
async def event_sharing_group(db, organisation, site_admin_user, sharing_group):
    event = Event(
        org_id=organisation.id,
        orgc_id=organisation.id,
        user_id=site_admin_user.id,
        uuid=libuuid.uuid4(),
        sharing_group_id=sharing_group.id,
        threat_level_id=1,
        info="event_published_sharing_group",
        date=date(year=2024, month=2, day=13),
        analysis=1,
        distribution=EventDistributionLevels.SHARING_GROUP,
        published=True,
    )
    async with DBManager(db, event) as obj:
        await db.commit()
        yield obj
    await db.commit()


@pytest_asyncio.fixture
async def sighting(db, organisation, event_with_attributes):
    attribute: Attribute = event_with_attributes.attributes[0]
    sighting: Sighting = generate_sighting(event_with_attributes.id, attribute.id, organisation.id)

    db.add(sighting)
    await db.commit()
    await db.refresh(sighting)

    yield {
        "sighting": sighting,
        "organisation": organisation,
        "event": event_with_attributes,
    }

    await db.delete(sighting)
    await db.commit()


@pytest_asyncio.fixture
async def event2(db, organisation, site_admin_user):
    event = Event(
        org_id=organisation.id,
        orgc_id=organisation.id,
        user_id=site_admin_user.id,
        uuid=libuuid.uuid4(),
        sharing_group_id=0,
        threat_level_id=1,
        info="event_published_sharing_group",
        date=date(year=2024, month=2, day=13),
        analysis=1,
        distribution=EventDistributionLevels.COMMUNITY,
        published=True,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)

    yield event

    await db.delete(event)
    await db.commit()


@pytest_asyncio.fixture
async def attribute(db, event):
    event_id = event.id
    attribute = generate_attribute(event_id)
    event.attribute_count += 1

    db.add(attribute)
    await db.commit()
    await db.refresh(attribute)

    yield attribute
    await db.refresh(event)

    await db.delete(attribute)
    event.attribute_count -= 1
    await db.commit()


@pytest_asyncio.fixture
async def attribute2(db, event):
    event_id = event.id
    attribute = generate_attribute(event_id)

    db.add(attribute)
    await db.commit()
    await db.refresh(attribute)

    yield attribute

    await db.delete(attribute)
    await db.commit()


@pytest_asyncio.fixture
async def attribute_multi(db, event):
    event_id = event.id
    attribute = Attribute(value="1.2.3.4|80", type="ip-src|port", category="Network activity", event_id=event_id)

    db.add(attribute)
    await db.commit()
    await db.refresh(attribute)

    yield attribute

    await db.delete(attribute)
    await db.commit()


@pytest_asyncio.fixture
async def attribute_multi2(db, event):
    event_id = event.id
    attribute = Attribute(value="2.3.4.5|80", type="ip-src|port", category="Network activity", event_id=event_id)

    db.add(attribute)
    await db.commit()
    await db.refresh(attribute)

    yield attribute

    await db.delete(attribute)
    await db.commit()


@pytest_asyncio.fixture
async def tag(db, site_admin_user):
    tag = generate_tag()

    tag.user_id = site_admin_user.id
    tag.org_id = site_admin_user.org_id
    tag.is_galaxy = True
    tag.exportable = True

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    yield tag

    await db.delete(tag)
    await db.commit()


@pytest_asyncio.fixture
async def shadow_attribute(db, organisation, event):
    shadow_attribute = generate_shadow_attribute(organisation.id, event.id, event.uuid, event.org_id)

    db.add(shadow_attribute)
    await db.commit()
    await db.refresh(shadow_attribute)

    yield shadow_attribute

    await db.delete(shadow_attribute)
    await db.commit()


@pytest_asyncio.fixture
async def shadow_attribute_with_organisation_event(db, organisation, event):
    shadow_attribute = generate_shadow_attribute(organisation.id, event.id, event.uuid, event.org_id)

    db.add(shadow_attribute)
    await db.commit()
    await db.refresh(shadow_attribute)

    yield {
        "shadow_attribute": shadow_attribute,
        "organisation": organisation,
        "event": event,
    }

    await db.delete(shadow_attribute)
    await db.commit()


@pytest_asyncio.fixture
async def sharing_group(db, instance_owner_org):
    sharing_group = generate_sharing_group()
    sharing_group.organisation_uuid = instance_owner_org.uuid
    sharing_group.org_id = instance_owner_org.id

    db.add(sharing_group)
    await db.flush()

    sgo = SharingGroupOrg(sharing_group_id=sharing_group.id, org_id=instance_owner_org.id)
    db.add(sgo)

    await db.flush()
    await db.commit()

    yield sharing_group

    await db.delete(sgo)
    await db.delete(sharing_group)
    await db.commit()


@pytest_asyncio.fixture
async def sharing_group2(db, instance_org_two):
    sharing_group = generate_sharing_group()
    sharing_group.organisation_uuid = instance_org_two.uuid
    sharing_group.org_id = instance_org_two.id

    db.add(sharing_group)
    await db.commit()
    await db.refresh(sharing_group)

    yield sharing_group

    await db.delete(sharing_group)
    await db.commit()


@pytest_asyncio.fixture
async def server(db, instance_owner_org):
    server = generate_server()
    server.org_id = instance_owner_org.id

    db.add(server)
    await db.commit()
    yield server

    await db.delete(server)
    await db.commit()


@pytest_asyncio.fixture
async def galaxy(db):
    galaxy = Galaxy(
        name="test galaxy",
        type="test type",
        description="test",
        version="version",
        kill_chain_order="test kill_chain_order",
        org_id=0,
        orgc_id=0,
        distribution=DistributionLevels.ALL_COMMUNITIES,
        created=datetime.now(),
        modified=datetime.now(),
    )

    db.add(galaxy)
    await db.commit()
    await db.refresh(galaxy)

    yield galaxy

    await db.delete(galaxy)
    await db.commit()


@pytest_asyncio.fixture(name="auth_key")
async def fixture_auth_key(db, site_admin_user):
    async for e in auth_key(db, site_admin_user):
        yield e


async def auth_key(db, site_admin_user):
    clear_key = "siteadminuser".ljust(40, "0")

    auth_key = AuthKey(
        authkey=hash_secret(clear_key),
        authkey_start=clear_key[:4],
        authkey_end=clear_key[-4:],
        comment="test comment",
        user_id=site_admin_user.id,
    )
    async with DBManager(db, auth_key) as obj:
        await db.commit()
        yield clear_key, obj
    await db.commit()


@pytest.fixture
def galaxy_cluster_collection_uuid():
    return uuid()


@pytest.fixture
def galaxy_default_cluster_one_uuid():
    return uuid()


@pytest.fixture
def galaxy_default_cluster_two_uuid():
    return uuid()


@pytest.fixture
def galaxy_cluster_one_uuid():
    return uuid()


@pytest.fixture
def galaxy_cluster_two_uuid():
    return uuid()


@pytest_asyncio.fixture
async def test_default_galaxy(db, galaxy_default_cluster_one_uuid, galaxy_default_cluster_two_uuid, organisation):
    async with AsyncExitStack() as stack:

        async def add_to_db(elem):
            return await stack.enter_async_context(DBManager(db, elem))

        galaxy = await add_to_db(
            Galaxy(
                namespace="misp",
                name="test galaxy",
                type="test galaxy type",
                description="test",
                version="1",
                kill_chain_order=None,
                uuid=uuid(),
                enabled=True,
                local_only=False,
                org_id=0,
                orgc_id=0,
                distribution=DistributionLevels.ALL_COMMUNITIES,
                created=datetime.now(),
                modified=datetime.now(),
            )
        )

        galaxy_cluster = await add_to_db(
            GalaxyCluster(
                uuid=galaxy_default_cluster_one_uuid,
                collection_uuid="",
                type="test galaxy type",
                value="test",
                tag_name=galaxy_tag_name("test galaxy type", galaxy_cluster_one_uuid),
                description="test",
                galaxy_id=galaxy.id,
                source="me",
                authors=["Konstantin Zangerle", "Test Writer"],
                version=1,
                distribution=3,
                sharing_group_id=0,
                org_id=0,
                orgc_id=0,
                default=1,
                locked=0,
                extends_uuid="",
                extends_version=0,
                published=True,
                deleted=False,
            )
        )

        galaxy_cluster2 = await add_to_db(
            GalaxyCluster(
                uuid=galaxy_default_cluster_two_uuid,
                collection_uuid="",
                type="test galaxy type",
                value="test",
                tag_name=galaxy_tag_name("test galaxy type", galaxy_cluster_two_uuid),
                description="test",
                galaxy_id=galaxy.id,
                source="me",
                authors=["Konstantin Zangerle", "Test Writer"],
                version=1,
                distribution=3,
                sharing_group_id=0,
                org_id=0,
                orgc_id=0,
                default=1,
                locked=0,
                extends_uuid="",
                extends_version=0,
                published=True,
                deleted=False,
            )
        )

        galaxy_element = GalaxyElement(
            galaxy_cluster_id=galaxy_cluster.id, key="refs", value="http://test-one-one.example.com"
        )
        galaxy_element2 = GalaxyElement(
            galaxy_cluster_id=galaxy_cluster.id, key="refs", value="http://test-one-two.example.com"
        )

        galaxy_element21 = GalaxyElement(
            galaxy_cluster_id=galaxy_cluster2.id, key="refs", value="http://test-two-one.example.com"
        )
        galaxy_element22 = GalaxyElement(
            galaxy_cluster_id=galaxy_cluster2.id, key="refs", value="http://test-two-two.example.com"
        )

        galaxy_elements = (galaxy_element, galaxy_element2, galaxy_element21, galaxy_element22)
        for g_e in galaxy_elements:
            db.add(g_e)

        await db.commit()

        for g_e in galaxy_elements:
            await db.refresh(g_e)

        yield {
            "galaxy": galaxy,
            "galaxy_cluster": galaxy_cluster,
            "galaxy_cluster2": galaxy_cluster2,
            "galaxy_element": galaxy_element,
            "galaxy_element2": galaxy_element2,
            "galaxy_element21": galaxy_element21,
            "galaxy_element22": galaxy_element22,
        }
        await db.commit()

        # if a galaxy cluster is edited, new elements are created with new IDs, therefore we need this
        qry = delete(GalaxyElement).where(GalaxyElement.galaxy_cluster_id.in_([galaxy_cluster.id, galaxy_cluster2.id]))
        await db.execute(qry)


@pytest_asyncio.fixture
async def test_galaxy(db, galaxy_cluster_one_uuid, galaxy_cluster_two_uuid, organisation):
    async with AsyncExitStack() as stack:

        async def add_to_db(elem):
            return await stack.enter_async_context(DBManager(db, elem))

        galaxy = await add_to_db(
            Galaxy(
                namespace="misp",
                name="test galaxy",
                type="test galaxy type",
                description="test",
                version="1",
                kill_chain_order=None,
                uuid=uuid(),
                enabled=True,
                local_only=False,
                org_id=0,
                orgc_id=0,
                distribution=DistributionLevels.ALL_COMMUNITIES,
                created=datetime.now(),
                modified=datetime.now(),
            )
        )

        galaxy_cluster = await add_to_db(
            GalaxyCluster(
                uuid=galaxy_cluster_one_uuid,
                collection_uuid="",
                type="test galaxy type",
                value="test",
                tag_name=galaxy_tag_name("test galaxy type", galaxy_cluster_one_uuid),
                description="test",
                galaxy_id=galaxy.id,
                source="me",
                authors=["Konstantin Zangerle", "Test Writer"],
                version=1,
                distribution=3,
                sharing_group_id=0,
                org_id=organisation.id,
                orgc_id=organisation.id,
                default=0,
                locked=0,
                extends_uuid="",
                extends_version=0,
                published=True,
                deleted=False,
            )
        )

        galaxy_cluster2 = await add_to_db(
            GalaxyCluster(
                uuid=galaxy_cluster_two_uuid,
                collection_uuid="",
                type="test galaxy type",
                value="test",
                tag_name=galaxy_tag_name("test galaxy type", galaxy_cluster_two_uuid),
                description="test",
                galaxy_id=galaxy.id,
                source="me",
                authors=["Konstantin Zangerle", "Test Writer"],
                version=1,
                distribution=3,
                sharing_group_id=0,
                org_id=organisation.id,
                orgc_id=organisation.id,
                default=0,
                locked=0,
                extends_uuid="",
                extends_version=0,
                published=True,
                deleted=False,
            )
        )

        galaxy_element = GalaxyElement(
            galaxy_cluster_id=galaxy_cluster.id, key="refs", value="http://test-one-one.example.com"
        )
        galaxy_element2 = GalaxyElement(
            galaxy_cluster_id=galaxy_cluster.id, key="refs", value="http://test-one-two.example.com"
        )

        galaxy_element21 = GalaxyElement(
            galaxy_cluster_id=galaxy_cluster2.id, key="refs", value="http://test-two-one.example.com"
        )
        galaxy_element22 = GalaxyElement(
            galaxy_cluster_id=galaxy_cluster2.id, key="refs", value="http://test-two-two.example.com"
        )

        galaxy_elements = (galaxy_element, galaxy_element2, galaxy_element21, galaxy_element22)
        for g_e in galaxy_elements:
            db.add(g_e)

        await db.commit()

        for g_e in galaxy_elements:
            await db.refresh(g_e)

        yield {
            "galaxy": galaxy,
            "galaxy_cluster": galaxy_cluster,
            "galaxy_cluster2": galaxy_cluster2,
            "galaxy_element": galaxy_element,
            "galaxy_element2": galaxy_element2,
            "galaxy_element21": galaxy_element21,
            "galaxy_element22": galaxy_element22,
        }
        await db.commit()

        # if a galaxy cluster is edited, new elements are created with new IDs, therefore we need this
        qry = delete(GalaxyElement).where(GalaxyElement.galaxy_cluster_id.in_([galaxy_cluster.id, galaxy_cluster2.id]))
        await db.execute(qry)


@pytest_asyncio.fixture()
async def galaxy_cluster_one_tag(db, galaxy_cluster_one_uuid):
    tag = Tag(
        name=galaxy_tag_name("test galaxy type", galaxy_cluster_one_uuid),
        colour="#123456",
        exportable=True,
        hide_tag=False,
        numerical_value=None,
        local_only=False,
        user_id=0,
        org_id=0,
        is_galaxy=True,
        is_custom_galaxy=True,
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    yield tag

    await db.delete(tag)
    await db.commit()


@pytest_asyncio.fixture()
async def galaxy_cluster_two_tag(db):
    tag = Tag(
        name='misp-galaxy:test="two"',
        colour="#123456",
        exportable=True,
        hide_tag=False,
        numerical_value=None,
        local_only=False,
        user_id=0,
        org_id=0,
        is_galaxy=True,
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    yield tag

    await db.delete(tag)
    await db.commit()


@pytest_asyncio.fixture()
async def normal_tag(db, instance_owner_org):
    tag = Tag(
        name="test normal tag",
        colour="#123456",
        exportable=True,
        hide_tag=False,
        numerical_value=None,
        local_only=False,
        user_id=0,
        org_id=0,
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    yield tag

    await db.delete(tag)
    await db.commit()


@pytest_asyncio.fixture()
async def local_only_tag(db, instance_owner_org):
    tag = Tag(
        name="test local only tag",
        colour="#123456",
        exportable=True,
        hide_tag=False,
        numerical_value=1,
        local_only=True,
        user_id=1,
        org_id=instance_owner_org.id,
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    yield tag

    await db.delete(tag)
    await db.commit()


@pytest_asyncio.fixture()
async def non_exportable_local_only_tag(db, instance_owner_org):
    tag = Tag(
        name="test non exportable local only tag",
        colour="#123456",
        exportable=False,
        hide_tag=False,
        numerical_value=1,
        local_only=True,
        user_id=1,
        org_id=instance_owner_org.id,
    )

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    yield tag

    await db.delete(tag)
    await db.commit()


@pytest_asyncio.fixture()
async def attribute_with_normal_tag(db, attribute, normal_tag):
    assert not normal_tag.local_only
    qry = (
        select(Attribute)
        .filter(Attribute.id == attribute.id)
        .options(selectinload(Attribute.attributetags))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)
    at = await attribute.add_tag(db, normal_tag)
    assert not at.local

    await db.commit()
    await db.refresh(attribute)

    yield attribute, at

    await db.delete(at)
    await db.commit()


@pytest_asyncio.fixture()
async def attribute_with_normal_tag_local(db, attribute, normal_tag):
    assert not normal_tag.local_only
    qry = (
        select(Attribute)
        .filter(Attribute.id == attribute.id)
        .options(selectinload(Attribute.attributetags))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)
    at = await attribute.add_tag(db, normal_tag, local=True)

    await db.commit()
    await db.refresh(attribute)

    yield attribute, at

    await db.delete(at)
    await db.commit()


@pytest_asyncio.fixture()
async def attribute_with_local_tag(db, attribute, local_only_tag):
    qry = (
        select(Attribute)
        .filter(Attribute.id == attribute.id)
        .options(selectinload(Attribute.attributetags))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)
    at = await attribute.add_tag(db, local_only_tag)
    assert at.local

    await db.commit()
    await db.refresh(attribute)

    yield attribute

    await db.delete(at)
    await db.commit()


@pytest_asyncio.fixture()
async def attribute_with_non_exportable_local_tag(db, attribute, non_exportable_local_only_tag):
    assert non_exportable_local_only_tag.local_only
    qry = (
        select(Attribute)
        .filter(Attribute.id == attribute.id)
        .options(selectinload(Attribute.attributetags))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)
    at = await attribute.add_tag(db, non_exportable_local_only_tag)

    await db.commit()
    await db.refresh(attribute)

    yield attribute

    await db.delete(at)
    await db.commit()


@pytest_asyncio.fixture()
async def attribute_with_galaxy_cluster_one_tag(db, attribute, galaxy_cluster_one_tag, test_galaxy):
    assert not galaxy_cluster_one_tag.local_only
    qry = (
        select(Attribute)
        .filter(Attribute.id == attribute.id)
        .options(selectinload(Attribute.attributetags))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)
    at = await attribute.add_tag(db, galaxy_cluster_one_tag)
    assert not at.local

    await db.commit()
    await db.refresh(attribute)

    yield attribute

    await db.delete(at)
    await db.commit()


@pytest_asyncio.fixture()
async def event_with_normal_tag(db, event, normal_tag):
    assert not normal_tag.local_only

    event_tag: EventTag = await event.add_tag(db, normal_tag)
    assert not event_tag.local

    await db.commit()
    await db.refresh(event)
    qry = (
        select(Event)
        .filter(Event.id == event.id)
        .options(selectinload(Event.eventtags))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)

    yield event, event_tag

    await db.delete(event_tag)
    await db.commit()


@pytest_asyncio.fixture()
async def event_with_normal_tag_local(db, event, normal_tag):
    assert not normal_tag.local_only

    event_tag: EventTag = await event.add_tag(db, normal_tag, local=True)

    await db.commit()
    await db.refresh(event)
    qry = (
        select(Event)
        .filter(Event.id == event.id)
        .options(selectinload(Event.eventtags))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)

    yield event

    await db.delete(event_tag)
    await db.commit()


@pytest_asyncio.fixture()
async def event_with_attributes(db, event):
    event_id = event.id
    attribute = generate_attribute(event_id)
    attribute_2 = generate_attribute(event_id)
    event.attribute_count += 2

    db.add(attribute)
    db.add(attribute_2)
    await db.commit()
    await db.refresh(event)

    qry = (
        select(Event)
        .filter(Event.id == event_id)
        .options(selectinload(Event.attributes))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)

    await db.refresh(attribute)
    await db.refresh(attribute_2)

    yield event

    await db.delete(attribute)
    await db.delete(attribute_2)
    event.attribute_count -= 2

    await db.commit()


@pytest_asyncio.fixture()
async def two_event_with_same_attribute_values(db, event, event2):
    event_id = event.id
    event2_id = event2.id

    assert event_id != event2_id

    attribute = generate_attribute(event_id)
    attribute2 = generate_attribute(event2_id)

    db.add(attribute)
    db.add(attribute2)

    await db.commit()
    await db.refresh(attribute)
    await db.refresh(attribute2)

    assert attribute.value == attribute2.value
    assert attribute.event_id == event_id
    assert attribute2.event_id == event2_id

    qry = (
        select(Event)
        .filter(Event.id == event.id)
        .options(selectinload(Event.attributes))
        .execution_options(populate_existing=True)
    )
    qry2 = (
        select(Event)
        .filter(Event.id == event2.id)
        .options(selectinload(Event.attributes))
        .execution_options(populate_existing=True)
    )
    await db.execute(qry)
    await db.execute(qry2)

    await db.commit()

    yield [(event, attribute), (event2, attribute2)]

    await db.delete(attribute)
    await db.delete(attribute2)
    await db.commit()


@pytest_asyncio.fixture()
async def post(db):
    post: Post = generate_post()
    db.add(post)
    await db.commit()
    await db.refresh(post)

    yield post

    await db.delete(post)
    await db.commit()


@pytest_asyncio.fixture()
async def over_correlating_value(db):
    ocv: OverCorrelatingValue = generate_over_correlating_value()
    db.add(ocv)
    await db.commit()
    await db.refresh(ocv)

    yield ocv

    await db.delete(ocv)
    await db.commit()


@pytest_asyncio.fixture()
async def correlating_value(db):
    cv: CorrelationValue = generate_correlation_value()
    db.add(cv)
    await db.commit()
    await db.refresh(cv)

    yield cv
    await db.commit()

    await db.delete(cv)
    await db.commit()


@pytest_asyncio.fixture()
async def correlating_values(db):
    list_c_v: list[CorrelationValue] = []

    for i in range(3):
        c_v: CorrelationValue = generate_correlation_value()
        db.add(c_v)
        await db.commit()
        await db.refresh(c_v)

        list_c_v.append(c_v)

    yield list_c_v

    for list_c_v_item in list_c_v:
        await db.delete(list_c_v_item)
        await db.commit()


@pytest_asyncio.fixture()
async def over_correlating_values(db):
    list_o_c_v: list[OverCorrelatingValue] = []

    for i in range(3):
        list_o_c_v.append(generate_over_correlating_value())
        db.add(list_o_c_v[i])
        await db.commit()
        await db.refresh(list_o_c_v[i])

    yield list_o_c_v

    for list_o_c_v_item in list_o_c_v:
        await db.delete(list_o_c_v_item)
        await db.commit()


@pytest_asyncio.fixture
async def correlation_exclusion(db):
    exclusion: CorrelationExclusions = generate_correlation_exclusions()

    db.add(exclusion)
    await db.commit()
    await db.refresh(exclusion)

    yield exclusion

    await db.delete(exclusion)
    await db.commit()


@pytest_asyncio.fixture()
async def correlation_exclusions(db):
    list_exclusions: list[CorrelationExclusions] = []

    list_exclusions = [generate_correlation_exclusions() for _ in range(3)]

    for ex in list_exclusions:
        db.add(ex)
    await db.commit()

    for ex in list_exclusions:
        await db.refresh(ex)

    yield list_exclusions

    for exclusion in list_exclusions:
        await db.delete(exclusion)
        await db.commit()


@pytest_asyncio.fixture()
async def object1(db, event, sharing_group):
    misp_object: Object = generate_object()
    misp_object.event_id = event.id
    misp_object.sharing_group_id = sharing_group.id
    misp_object.distribution = AttributeDistributionLevels.SHARING_GROUP

    db.add(misp_object)
    await db.commit()
    await db.refresh(misp_object)

    yield misp_object

    await db.delete(misp_object)
    await db.commit()


@pytest_asyncio.fixture()
async def object2(db, event, sharing_group):
    misp_object: Object = generate_object()
    misp_object.event_id = event.id
    misp_object.sharing_group_id = sharing_group.id
    misp_object.distribution = AttributeDistributionLevels.SHARING_GROUP

    db.add(misp_object)
    await db.commit()
    await db.refresh(misp_object)

    yield misp_object

    await db.delete(misp_object)
    await db.commit()


@pytest_asyncio.fixture()
async def default_correlation(db, correlating_value):
    dc: DefaultCorrelation = generate_default_correlation()
    dc.value_id = correlating_value.id

    db.add(dc)
    await db.commit()
    await db.refresh(dc)

    yield dc

    await db.delete(dc)
    await db.commit()


@pytest_asyncio.fixture()
async def user(db, instance_owner_org, site_admin_role):
    user = generate_user()

    user.org_id = instance_owner_org.id
    user.server_id = 0
    user.role_id = site_admin_role.id

    db.add(user)
    await db.commit()
    await db.refresh(user)

    yield user

    await db.delete(user)
    await db.commit()


@pytest_asyncio.fixture()
async def event_blocklist(db, event):
    event_blocklist = generate_event_blocklist(event.uuid, event.info, event.orgc_id)

    db.add(event_blocklist)
    await db.commit()
    await db.refresh(event_blocklist)

    yield event_blocklist

    await db.delete(event_blocklist)
    await db.commit()


@pytest_asyncio.fixture()
async def org_blocklist(db, organisation):
    org_blocklist = generate_org_blocklist(organisation.id, organisation.name)

    db.add(org_blocklist)
    await db.commit()
    await db.refresh(org_blocklist)

    yield org_blocklist

    await db.delete(org_blocklist)
    await db.commit()


@pytest_asyncio.fixture()
async def cluster_blocklist(db, test_galaxy):
    cluster = test_galaxy["galaxy_cluster"]
    cluster_blocklist: GalaxyClusterBlocklist = generate_galaxy_cluster_blocklist(cluster.uuid, cluster.orgc_id)

    db.add(cluster_blocklist)
    await db.commit()
    await db.refresh(cluster_blocklist)

    yield cluster_blocklist

    await db.delete(cluster_blocklist)
    await db.commit()


@pytest_asyncio.fixture
async def threat_level(db):
    threat_level: ThreatLevel = generate_threat_level()

    db.add(threat_level)
    await db.commit()
    await db.refresh(threat_level)

    yield threat_level

    await db.delete(threat_level)
    await db.commit()
