from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from telegram.helpers import escape_markdown

from mdabojbot.prediction.service import (
    create_prediction,
    get_random_prediction,
    get_unapproved_predictions,
    prediction_approve,
    prediction_delete,
)
from mdabojbot.user.service import get_random_admin, is_user_admin


async def add_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Save prediction from user."""
    if not update.effective_chat:
        raise RuntimeError("This update has no chat associated with it.")
    if not update.effective_user:
        raise RuntimeError("This update has no user associated with it.")

    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Нафига мне пустое предсказание? Ты бы хоть одно слово написал...",
        )
        return

    new_prediction = await create_prediction(
        telegram_user_id=update.effective_user.id,
        prediction_text=" ".join(context.args),
    )
    random_admin = await get_random_admin()
    admin_chat = await context.bot.get_chat(random_admin.telegram_user_id)

    username = update.effective_user.first_name
    if update.effective_user.username:
        username += f" @{escape_markdown(update.effective_user.username, version=2)}"

    await context.bot.send_message(
        chat_id=admin_chat.id,
        text=(
            f"Пользователь: {escape_markdown(username, version=2)}\n"
            f"Предлагает предсказание с ID `{new_prediction.id}`\n"
            f"`{escape_markdown(new_prediction.text, version=2)}`"
        ),
        parse_mode="MarkdownV2",
    )
    if update.effective_user.id != random_admin.telegram_user_id:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "Твоя писанина отправлена админу на проверку.\n"
                "Может быть он апрувнет, а может и нет. Кто знает..."
            ),
        )


async def what_my_future(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get random prediction for user."""
    if not update.effective_chat:
        raise RuntimeError("This update has no chat associated with it.")

    try:
        random_prediction = await get_random_prediction()
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Надо же. Нет ни одного предсказания в базе :(",
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=random_prediction.text,
        )


async def approve_prediction(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Approve prediction by admin."""
    if not update.effective_chat:
        raise RuntimeError("This update has no chat associated with it.")
    if not update.effective_user:
        raise RuntimeError("This update has no user associated with it.")

    if not is_user_admin(update.effective_user.id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Тише, тише маленький. Эта кнопочка для взрослых дядек",
        )
        return

    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Мне бы ID предсказания, чтобы я его апрувнул. А то так хз какое нужно",
        )
        return

    if len(context.args) != 1 and not context.args[0].isdigit():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Смотри. ID - это одна строчка с циферками и ничего лишнего. Попробуй еще раз",
        )
        return

    try:
        approved_prediction = await prediction_approve(int(context.args[0]))
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Я не знаю предсказания с таким ID :(",
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"Предсказание `{escape_markdown(approved_prediction.text, version=2)}` "
                f"апрувнуто"
            ),
            parse_mode="MarkdownV2",
        )


async def remove_prediction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete prediction by admin."""
    if not update.effective_chat:
        raise RuntimeError("This update has no chat associated with it.")
    if not update.effective_user:
        raise RuntimeError("This update has no user associated with it.")

    if not await is_user_admin(update.effective_user.id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Тише, тише маленький. Эта кнопочка для взрослых дядек",
        )
        return

    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Мне бы ID предсказания, чтобы я его апрувнул. А то так хз какое нужно",
        )
        return

    if len(context.args) != 1 or not context.args[0].isdigit():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Смотри. ID - это одна строчка с циферками и ничего лишнего. Попробуй еще раз",
        )
        return

    try:
        await prediction_delete(int(context.args[0]))
    except ValueError:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Я не знаю предсказания с таким ID :(",
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Предсказание удалено!",
        )


async def list_unapproved_predictions(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """List only unapproved predictions for admin."""
    if not update.effective_chat:
        raise RuntimeError("This update has no chat associated with it.")
    if not update.effective_user:
        raise RuntimeError("This update has no user associated with it.")

    if not is_user_admin(update.effective_user.id):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Тише, тише маленький. Эта кнопочка для взрослых дядек",
        )
        return

    unapproved_predictions = await get_unapproved_predictions()
    list_of_text = []
    for prediction in unapproved_predictions:
        list_of_text.append(
            f"\nID: `{prediction.id}`\nТекст: `{escape_markdown(prediction.text, version=2)}`"
        )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вот что имеем на сейчас:\n" + "\n".join(list_of_text),
        parse_mode="MarkdownV2",
    )


handlers = (
    CommandHandler("add_prediction", add_prediction),
    CommandHandler("what_my_future", what_my_future),
    CommandHandler("approve_prediction", approve_prediction),
    CommandHandler("remove_prediction", remove_prediction),
    CommandHandler("list_unapproved_predictions", list_unapproved_predictions),
)
