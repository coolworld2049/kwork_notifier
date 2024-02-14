from contextlib import suppress

from aiogram import F, Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User

from telegram_bot.common.keyboards.navigation import navigation_keyboard_builder
from telegram_bot.routers.callbacks import MenuCallback, FilterCallback

from telegram_bot.routers.filters.state import EditState
from telegram_bot.template_engine import render_template

router = Router(name=__file__)


async def settings_menu(bot: Bot, user: User):
    builder = ...
    builder = navigation_keyboard_builder(
        builder=builder,
        menu_callback=MenuCallback(name="start").pack(),
    )
    await bot.send_message(
        user.id,
        render_template("settings.html"),
        reply_markup=builder.as_markup(),
    )


@router.callback_query(MenuCallback.filter(F.name == "settings"))
async def settings_menu_callback(query: CallbackQuery, state: FSMContext):
    await settings_menu(query.bot, query.from_user)
    with suppress(TelegramBadRequest):
        await query.message.delete()


@router.callback_query(
    FilterCallback.filter(F.name == "settings" and F.action == "edit")
)
async def settings_edit(query: CallbackQuery, state: FSMContext):
    await query.answer("Enter new value e.g `key: value`")
    await state.set_state(EditState.edit)


@router.message(EditState.edit)
async def settings_edit_message(message: Message, state: FSMContext):
    item = message.text.split(": ")
    ...
    with suppress(TelegramBadRequest):
        await message.delete_message(message.from_user.id, message.message_id - 1)
        await message.delete()
    await state.clear()
    await settings_menu(message.bot, message.from_user)
