from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from telegram.ext import Application

from mdabojbot import utils
from mdabojbot.common.models import BaseModel
from mdabojbot.user.constants import UserGroup

engine = create_async_engine(f"sqlite+aiosqlite:///{utils.get_path_to_db()}", echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)


def make_db_session(method):
    """Decorator for easy ORM queries without session handler."""

    async def wrapper(*args, **kwargs):
        # NOTE: The session can be passed as argument to decorated function directly
        # or implicitly using this decorator
        session = kwargs.pop("session", async_session())

        try:
            return await method(*args, session=session, **kwargs)
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

    return wrapper


async def init_db(application: Application):
    # TODO: Maybe change to something beautiful?
    from mdabojbot.prediction.models import Prediction  # noqa
    from mdabojbot.user.models import User  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    superuser_telegram_id = utils.get_superuser_telegram_id()
    async with async_session() as session:
        query = select(User).where(User.telegram_user_id == superuser_telegram_id)
        result = await session.execute(query)
        existing_superuser = result.scalar_one_or_none()
        if not existing_superuser:
            new_superuser = User(
                telegram_user_id=superuser_telegram_id, group=UserGroup.ADMIN
            )
            session.add(new_superuser)
            await session.commit()
