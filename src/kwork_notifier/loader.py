from aiogram import Bot
from aiogram.enums import ParseMode

from kwork_notifier.settings import settings

bot = Bot(
    token=settings.BOT_TOKEN,
    parse_mode=ParseMode.HTML,
    disable_web_page_preview=True,
)
