from aiogram.filters.callback_data import CallbackData


class MenuCallback(CallbackData, prefix="menu"):
    name: str
    action: str | None = None
    message_id: int | None = None


class FilterCallback(CallbackData, prefix="filter"):
    name: str
    action: str | None = None
