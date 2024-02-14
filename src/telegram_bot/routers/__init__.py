from aiogram import Router

from telegram_bot.routers import menu
from telegram_bot.routers import filters

main_router = Router()
main_router.include_routers(
    filters.router,
    menu.router,
)
