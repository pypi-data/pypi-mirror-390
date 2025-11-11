from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.db.models.admin_setting import AdminSetting
from mmisp.db.models.user_setting import UserSetting


async def get_admin_setting(db: AsyncSession, setting_name: str) -> str | None:
    setting_db = await db.execute(select(AdminSetting.value).where(AdminSetting.setting == setting_name))
    return setting_db.scalars().one_or_none()


async def set_admin_setting(db: AsyncSession, setting_name: str, value: str) -> None:
    current_setting = await get_admin_setting(db, setting_name)
    if current_setting is None:
        new_setting = AdminSetting(setting=setting_name, value=value)
        db.add(new_setting)
    else:
        await db.execute(update(AdminSetting).where(AdminSetting.setting == setting_name).values(value=value))
    await db.flush()


async def get_user_setting(db: AsyncSession, setting_name: str, user_id: int) -> str | None:
    setting_db = await db.execute(
        select(UserSetting.value).where(UserSetting.setting == setting_name, UserSetting.user_id == user_id)
    )
    return setting_db.scalars().one_or_none()


async def set_user_setting(db: AsyncSession, setting_name: str, user_id: int, value: str) -> None:
    current_setting = await get_user_setting(db, setting_name, user_id)
    if current_setting is None:
        new_setting = UserSetting(setting=setting_name, user_id=user_id, value=value)
        db.add(new_setting)
    else:
        await db.execute(
            update(UserSetting)
            .where(UserSetting.setting == setting_name, UserSetting.user_id == user_id)
            .values(value=value)
        )
    await db.flush()
