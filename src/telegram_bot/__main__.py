import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from _logging import configure_logging
from telegram_bot.middlewares.acl import ACLMiddleware
from telegram_bot.middlewares.retry_request import RetryRequestMiddleware
from telegram_bot.routers import main_router
from telegram_bot.services.apscheduler import scheduler
from telegram_bot.settings import Settings
from telegram_bot.settings import settings


async def on_startup(
    bot: Bot,
    settings: Settings,
    scheduler: AsyncIOScheduler,
):
    commands = [
        BotCommand(command="/start", description="start bot"),
        BotCommand(command="/help", description="get help"),
    ]
    await bot.delete_my_commands()
    await bot.set_my_commands(commands)
    # scheduler.add_job(
    #     ..., "interval", minutes=10, kwargs={"bot": bot, "settings": settings}
    # )
    scheduler.start()


async def on_shutdown(
    bot: Bot,
    settings: Settings,
    scheduler: AsyncIOScheduler,
):
    await bot.delete_webhook(drop_pending_updates=True)
    scheduler.shutdown(wait=False)


def create_bot(settings: Settings) -> Bot:
    session: AiohttpSession = AiohttpSession()
    session.middleware(RetryRequestMiddleware())
    return Bot(
        token=settings.BOT_TOKEN,
        parse_mode=ParseMode.HTML,
        session=session,
        disable_web_page_preview=True,
    )


async def main():
    settings = Settings()

    bot = create_bot(settings)

    dp = Dispatcher()
    dp["settings"] = settings
    dp["scheduler"] = scheduler

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(main_router)

    dp.callback_query.middleware(CallbackAnswerMiddleware())
    dp.update.middleware(ACLMiddleware())

    await dp.start_polling(bot)


if __name__ == "__main__":
    configure_logging(settings.LOG_LEVEL)
    asyncio.run(main())
