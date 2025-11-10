from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mdabojbot.db import make_db_session
from mdabojbot.prediction.models import Prediction


@make_db_session
async def create_prediction(
    telegram_user_id: int, prediction_text: str, session: AsyncSession = AsyncSession()
) -> Prediction:
    new_prediction = Prediction(
        telegram_user_id=telegram_user_id,
        text=prediction_text,
        is_approved=False,
    )
    session.add(new_prediction)
    await session.commit()
    return new_prediction


@make_db_session
async def get_unapproved_predictions(
    session: AsyncSession = AsyncSession(),
) -> Sequence[Prediction]:
    query = select(Prediction).where(~Prediction.is_approved)
    result = await session.execute(query)
    return result.scalars().all()


@make_db_session
async def prediction_delete(
    prediction_id: int, session: AsyncSession = AsyncSession()
) -> None:
    query = select(Prediction).where(Prediction.id == prediction_id)
    result = await session.execute(query)
    prediction_to_delete = result.scalar_one_or_none()
    if not prediction_to_delete:
        raise ValueError(f"There is no prediction with id={prediction_id}!")
    await session.delete(prediction_to_delete)
    await session.commit()


@make_db_session
async def get_random_prediction(session: AsyncSession = AsyncSession()) -> Prediction:
    query = (
        select(Prediction)
        .where(Prediction.is_approved)
        .order_by(func.random())
        .limit(1)
    )
    result = await session.execute(query)
    random_prediction = result.scalar_one_or_none()
    if not random_prediction:
        raise ValueError("There is no approved prediction!")
    return random_prediction


@make_db_session
async def prediction_approve(
    prediction_id: int, session: AsyncSession = AsyncSession()
) -> Prediction:
    query = select(Prediction).where(Prediction.id == prediction_id)
    result = await session.execute(query)
    prediction_to_approve = result.scalar_one_or_none()
    if not prediction_to_approve:
        raise ValueError(f"There is no prediction with id={prediction_id}!")

    prediction_to_approve.is_approved = True
    await session.commit()
    await session.refresh(prediction_to_approve)
    return prediction_to_approve
