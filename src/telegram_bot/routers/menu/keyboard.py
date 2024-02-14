from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from telegram_bot.routers.callbacks import MenuCallback


def menu_keyboard_builder():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="filters",
            callback_data=MenuCallback(
                name="filters",
            ).pack(),
        ),
    )
    builder.adjust(1, 1)
    builder.add(
        InlineKeyboardButton(
            text="start notifier",
            callback_data=MenuCallback(
                name="start_notifier",
            ).pack(),
        ),
        InlineKeyboardButton(
            text="stop notifier",
            callback_data=MenuCallback(
                name="start_notifier",
            ).pack(),
        ),
    )
    builder.adjust(1, 2)
    return builder
