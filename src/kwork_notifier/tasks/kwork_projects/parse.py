import asyncio
import random
from datetime import timedelta

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from cashews import cache
from selectolax.lexbor import LexborHTMLParser

from kwork_api_client.kwork import Kwork
from kwork_api_client.types import Project
from kwork_notifier.loader import bot
from kwork_notifier.settings import settings
from kwork_notifier.template_engine import render_template


async def parse_kwork_projects():
    if not cache.is_setup():
        cache.setup(settings_url=settings.redis_url)
    kwork = Kwork(
        login=settings.KWORK_LOGIN,
        password=settings.KWORK_PASSWORD,
        phone_last=settings.KWORK_PHONE_LAST,
    )
    token = await kwork.token

    categories_ids = settings.KWORK_CATEGORIES

    raw_projects = await kwork.api_request(
        method="post",
        api_method="projects",
        categories=categories_ids,
        page=1,
        token=token,
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
        )

        projects.extend(get_projects(other_projects["response"]))

    for project in projects:
        project.description = LexborHTMLParser(project.description).text(
            separator="\n", strip=True
        )
        is_project_cached = await cache.get(f"kwork_project:{project.id}")
        if is_project_cached:
            continue
        inline_keyboard = InlineKeyboardBuilder()
        inline_keyboard.add(
            InlineKeyboardButton(
                text="Send offer",
                url=project.offer_url,
            )
        )
        await bot.send_message(
            chat_id=settings.BOT_NOTIFY_USER_ID,
            text=render_template("project.html", project=project.model_dump()),
            reply_markup=inline_keyboard.as_markup(),
        )
        await cache.set(
            f"kwork_project:{project.id}",
            value=project,
            expire=timedelta(hours=6).seconds,
        )
        await asyncio.sleep(random.choice([1, 2, 3]))

    await kwork.close()


if __name__ == "__main__":
    asyncio.run(parse_kwork_projects())
