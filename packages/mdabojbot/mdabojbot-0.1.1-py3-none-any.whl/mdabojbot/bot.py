import logging

from telegram.ext import ApplicationBuilder

from mdabojbot import db, utils
from mdabojbot.common.commands import handlers as common_commands
from mdabojbot.prediction.commands import handlers as prediction_commands

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def run():
    token = utils.get_token()
    application = ApplicationBuilder().token(token).post_init(db.init_db).build()
    application.add_handlers(
        (
            *prediction_commands,
            *common_commands,  # Always last
        )
    )
    application.run_polling()
