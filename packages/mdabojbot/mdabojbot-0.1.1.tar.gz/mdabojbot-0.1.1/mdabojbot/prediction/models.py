from sqlalchemy.orm import Mapped, mapped_column

from mdabojbot.common.models import BaseModel


class Prediction(BaseModel):
    __tablename__ = "prediction"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_user_id: Mapped[int]
    text: Mapped[str]
    is_approved: Mapped[bool]
