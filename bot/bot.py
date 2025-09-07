import logging
from typing import Dict

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from .config import TELEGRAM_TOKEN, REQUIRED_FIELDS
from .service_repository import (
    add_services,
    get_random_incomplete,
    update_service,
)
from .llm import parse_fields

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Здравствуйте! Нажмите 'Заполнить карточку', чтобы начать.",
        reply_markup=ReplyKeyboardMarkup([["Заполнить карточку"]], resize_keyboard=True),
    )


def render_card(card: Dict) -> str:
    lines = [f"Карточка: {card['name']}"]
    fields = card.get("fields", {})
    for f in REQUIRED_FIELDS:
        val = fields.get(f) or "<пусто>"
        lines.append(f"{f}: {val}")
    return "\n".join(lines)


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Использование: /add name1 name2 ...")
        return
    count = add_services(context.args)
    await update.message.reply_text(f"Добавлено {count} карточек")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "Заполнить карточку":
        card = get_random_incomplete()
        if not card:
            await update.message.reply_text("Все карточки заполнены!")
            return
        context.user_data["card"] = card
        await update.message.reply_text(render_card(card))
        await update.message.reply_text(
            "Введите данные для недостающих полей в формате key=value",
        )
        context.user_data["awaiting"] = True
    elif context.user_data.get("awaiting"):
        fields = parse_fields(text)
        if not fields:
            await update.message.reply_text("Не удалось распознать данные, попробуйте ещё раз")
            return
        context.user_data["parsed_fields"] = fields
        summary = "\n".join(f"{k}: {v}" for k, v in fields.items())
        await update.message.reply_text(
            f"Я понял так:\n{summary}\nВерно?",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Да", callback_data="yes"),
                        InlineKeyboardButton("Нет", callback_data="no"),
                    ]
                ]
            ),
        )
        context.user_data["awaiting"] = False
    else:
        await update.message.reply_text(
            "Не понимаю. Нажмите 'Заполнить карточку' чтобы начать.",
            reply_markup=ReplyKeyboardMarkup([["Заполнить карточку"]], resize_keyboard=True),
        )


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == "yes":
        card = context.user_data.get("card")
        fields = context.user_data.get("parsed_fields", {})
        if card and fields:
            update_service(card["_id"], fields)
            await query.edit_message_text("Сохранено")
        else:
            await query.edit_message_text("Нет данных для сохранения")
    else:
        await query.edit_message_text("Введите данные ещё раз")
        context.user_data["awaiting"] = True
        return
    # After handling, propose next card
    await query.message.reply_text(
        "Заполнить следующую?",
        reply_markup=ReplyKeyboardMarkup([["Заполнить карточку"]], resize_keyboard=True),
    )


def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_confirmation))

    app.run_polling()


if __name__ == "__main__":
    main()
