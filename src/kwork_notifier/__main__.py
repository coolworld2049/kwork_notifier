import asyncio

from aiogram import Bot, Dispatcher
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from cashews import cache

from kwork_notifier._logging import configure_logging
from kwork_notifier.loader import bot
from kwork_notifier.settings import Settings
from kwork_notifier.settings import settings
from kwork_notifier.tasks.kwork_projects.parse import parse_kwork_projects


async def on_startup(
    bot: Bot,
    settings: Settings,
    scheduler: AsyncIOScheduler,
):
    await bot.delete_my_commands()
    cache.setup(settings_url=settings.redis_url)
    scheduler.add_job(
        parse_kwork_projects,
        "interval",
        minutes=settings.SCHEDULE_PARSE_KWORK_MINUTES,
        id=parse_kwork_projects.__name__,
        replace_existing=True,
    )
    scheduler.start()


async def on_shutdown(
    bot: Bot,
    settings: Settings,
    scheduler: AsyncIOScheduler,
):
    await bot.delete_webhook(drop_pending_updates=True)
    scheduler.shutdown(wait=False)


async def main():
    settings = Settings()

    dp = Dispatcher()
    dp["settings"] = settings

    scheduler_jobstores = {
        "default": RedisJobStore(
            db=1, host=settings.REDIS_HOST, port=settings.REDIS_PORT
        )
    }
    scheduler = AsyncIOScheduler(jobstores=scheduler_jobstores)

    dp["scheduler"] = scheduler

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot)


if __name__ == "__main__":
    configure_logging(settings.LOG_LEVEL)
    asyncio.run(main())
