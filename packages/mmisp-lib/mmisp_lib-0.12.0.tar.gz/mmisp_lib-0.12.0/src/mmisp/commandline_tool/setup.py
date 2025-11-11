from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from mmisp.db.models.organisation import Organisation
from mmisp.db.models.role import Role
from mmisp.lib.standard_roles import get_standard_roles


async def setup(session: AsyncSession) -> None:
    for role in get_standard_roles():
        await add_role_if_not_exist(session, role)

    ghost_org = Organisation()
    ghost_org.name = "ghost_org"
    ghost_org.type = "ghost"
    ghost_org.nationality = "ghost"
    ghost_org.sector = "ghost"
    ghost_org.contacts = "ghost@example.com"
    ghost_org.landingpage = "ghost.example.com"
    ghost_org.local = True
    await add_organisation_if_not_exist(session, ghost_org)


async def add_role_if_not_exist(session: AsyncSession, role: Role) -> None:
    query = select(Role).where(Role.name == role.name)
    role_db = await session.execute(query)
    role_db = role_db.scalar_one_or_none()
    if role_db is None:
        session.add(role)
        await session.commit()


async def add_organisation_if_not_exist(session: AsyncSession, organisation: Organisation) -> None:
    query = select(Organisation).where(Organisation.name == organisation.name)
    organisation_db = await session.execute(query)
    organisation_db = organisation_db.scalar_one_or_none()
    if organisation_db is None:
        session.add(organisation)
        await session.commit()
