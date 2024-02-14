from contextlib import suppress

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import User, Message, CallbackQuery

from telegram_bot.routers.callbacks import MenuCallback
from telegram_bot.routers.menu.keyboard import menu_keyboard_builder
from telegram_bot.template_engine import render_template

router = Router(name=__file__)


async def start_cmd(bot: Bot, user: User, state: FSMContext, message_id: int):
    with suppress(TelegramBadRequest):
        await bot.delete_message(user.id, message_id - 1)
    await state.clear()
    await bot.send_message(
        user.id,
        render_template(
            "start.html",
            user=user.username,
            bot=await bot.me(),
        ),
        reply_markup=menu_keyboard_builder().as_markup(),
    )


@router.message(Command("start"))
async def start_message(message: Message, state: FSMContext):
    await start_cmd(message.bot, message.from_user, state, message.message_id)


@router.callback_query(MenuCallback.filter(F.name == "start"))
async def start_callback(
    query: CallbackQuery,
    state: FSMContext,
):
    with suppress(TelegramBadRequest):
        await query.message.delete()
    await start_cmd(query.bot, query.from_user, state, query.message.message_id)
