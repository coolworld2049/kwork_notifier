import asyncio
import random
from datetime import timedelta

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from cashews import cache
from loguru import logger
from selectolax.lexbor import LexborHTMLParser

from kwork_api_client.kwork import Kwork
from kwork_api_client.types import Project
from kwork_notifier.loader import bot
from kwork_notifier.settings import settings
from kwork_notifier.template_engine import render_template


async def parse_kwork_projects(check_if_project_cached: bool = True):
    if not cache.is_setup():
        cache.setup(settings_url=settings.redis_url)
    kwork = Kwork(
        login=settings.KWORK_LOGIN,
        password=settings.KWORK_PASSWORD,
        phone_last=settings.KWORK_PHONE_LAST,
    )
    token = await kwork.token

    categories_ids = settings.KWORK_CATEGORIES
    api_request_params = {
        "price_from": settings.KWORK_PRICE_FROM,
        "price_to": settings.KWORK_PRICE_TO,
        "hiring_from": settings.KWORK_HIRING_FROM,
        "kworks_filter_from": settings.KWORK_KWORKS_FILTER_TO,
        "kworks_filter_to": settings.KWORK_KWORKS_FILTER_TO,
    }
    raw_projects = await kwork.api_request(
        method="post",
        api_method="projects",
        categories=categories_ids,
        page=1,
        token=token,
        **api_request_params,
    )

    success = raw_projects["success"]
    if not success:
        return await kwork.close()

    def get_projects(response: list[dict]) -> list[Project]:
        result = [Project(**item) for item in response]
        return result

    projects = get_projects(raw_projects["response"])

    paging = raw_projects["paging"]
    pages = int((paging["pages"] + 1) / 2)

    for page in range(2, pages):
        other_projects = await kwork.api_request(
            method="post",
            api_method="projects",
            categories=categories_ids,
            page=page,
            token=token,
            **api_request_params,
        )

        projects.extend(get_projects(other_projects["response"]))

    sent_projects_count = 0
    cached_projects_count = 0
    for project in projects:
        project.description = LexborHTMLParser(project.description).text(
            separator="\n", strip=True
        )
        is_project_cached = await cache.get(f"kwork_project:{project.id}")
        if check_if_project_cached and is_project_cached:
            cached_projects_count += 1
            continue
        inline_keyboard = InlineKeyboardBuilder()
        inline_keyboard.add(
            InlineKeyboardButton(
                text="Send offer",
                url=project.offer_url,
            ),
            InlineKeyboardButton(
                text="User profile",
                url=project.customer_url,
            ),
        )
        await bot.send_message(
            chat_id=settings.BOT_NOTIFY_USER_ID,
            text=render_template("project.html", project=project),
            reply_markup=inline_keyboard.as_markup(),
        )
        await cache.set(
            f"kwork_project:{project.id}",
            value=project,
            expire=timedelta(hours=6).seconds,
        )
        sent_projects_count += 1
        await asyncio.sleep(random.choice([1, 2, 3]))

    logger.info(
        f"sent_projects_count={sent_projects_count} cached_projects_count={cached_projects_count}"
    )

    await kwork.close()


if __name__ == "__main__":
    asyncio.run(parse_kwork_projects(check_if_project_cached=False))
