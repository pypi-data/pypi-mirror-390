from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mdabojbot.db import make_db_session
from mdabojbot.user.constants import UserGroup
from mdabojbot.user.models import User


@make_db_session
async def get_random_admin(session: AsyncSession = AsyncSession()) -> User:
    query = (
        select(User)
        .where(User.group == UserGroup.ADMIN)
        .order_by(func.random())
        .limit(1)
    )
    result = await session.execute(query)
    random_admin = result.scalar_one_or_none()
    if not random_admin:
        raise ValueError("There is not admin!")
    return random_admin


@make_db_session
async def is_user_admin(
    telegram_user_id: int, session: AsyncSession = AsyncSession()
) -> bool:
    query = select(User).where(User.telegram_user_id == telegram_user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError(f"There is not user with id={telegram_user_id}")

    return user.group == UserGroup.ADMIN
