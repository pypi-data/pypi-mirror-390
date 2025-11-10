from sqlalchemy.orm import Mapped, mapped_column

from mdabojbot.common.models import BaseModel
from mdabojbot.user.constants import UserGroup


class User(BaseModel):
    """Users significant to the bot."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_user_id: Mapped[int]
    group: Mapped[UserGroup]
