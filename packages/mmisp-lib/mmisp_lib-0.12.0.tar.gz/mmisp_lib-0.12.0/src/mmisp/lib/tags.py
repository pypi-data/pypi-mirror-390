from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.db.models.tag import Tag
from mmisp.db.models.user import User
from mmisp.lib.permissions import Permission


async def get_or_create_instance_tag(
    db: AsyncSession, user: User, tag_name: str, ignore_permissions: bool, new_tag_local_only: bool, is_galaxy_tag: bool
) -> Tag:
    query = select(Tag).filter(func.lower(Tag.name) == func.lower(tag_name))
    res = await db.execute(query)
    tag = res.scalar_one_or_none()

    if tag is None:
        if not user.role.check_permission(Permission.TAG_EDITOR) and not ignore_permissions:
            raise ValueError("Missing permissions to create tag")

        tag = Tag(
            name=tag_name,
            colour="#0088cc",
            exportable=1,
            local_only=new_tag_local_only,
            org_id=0,
            user_id=0,
            hide_tag=0,
            is_galaxy=is_galaxy_tag,
        )
        db.add(tag)
        await db.flush()

        return tag

    if tag.user_id not in [0, user.id] or tag.org_id not in [0, user.org_id] or tag.is_galaxy != is_galaxy_tag:
        raise ValueError("Tag has wrong properties")

    return tag
