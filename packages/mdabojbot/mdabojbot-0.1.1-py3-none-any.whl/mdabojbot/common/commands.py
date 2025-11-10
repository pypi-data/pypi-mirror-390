import random

from telegram import Update
from telegram.constants import ChatType
from telegram.ext import ContextTypes, MessageHandler, filters


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat:
        raise RuntimeError("This update has no chat associated with it.")

    if update.effective_chat.type != ChatType.PRIVATE:
        return

    response_variants = (
        "Я в душе не чаю, что за херню ты написал.",
        "И что мне с этим делать?",
        "Я не понимаю эльфийский",
        "Так. А теперь еще раз, только подумай хорошо",
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=random.choice(response_variants),
    )


handlers = (MessageHandler(filters.COMMAND, unknown),)
