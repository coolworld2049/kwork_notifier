from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from loguru import logger

from telegram_bot.settings import settings


class ACLMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")
        if user.id not in settings.BOT_ACL_USER_IDS:
            logger.info(f"Access denied. User: {user.model_dump_json()}")
            return None
        return await handler(event, data)
