from datetime import datetime
from typing import List

from pydantic import BaseModel
from pytz import utc

from kwork_api_client.types.achievement import Achievement


class Project(BaseModel):
    id: int = None
    user_id: int = None
    username: str = None
    profile_picture: str = None
    price: int = None
    title: str = None
    description: str = None
    offers: int = None
    time_left: int = None
    parent_category_id: int = None
    category_id: int = None
    date_confirm: int = None
    category_base_price: int = None
    user_projects_count: int = None
    user_hired_percent: int = None
    achievements_list: List[Achievement] = None
    is_viewed: bool = None
    already_work: int = None
    allow_higher_price: bool = None
    possible_price_limit: int = None

    @property
    def url(self):
        return f"https://kwork.ru/projects/{self.id}"

    @property
    def offer_url(self):
        return f"https://kwork.ru/new_offer?project={self.id}"

    @classmethod
    def __convert_to_datetime(cls, timestamp: float):
        return datetime.fromtimestamp(timestamp, tz=utc)

    @property
    def time_left_datetime(self):
        return self.__convert_to_datetime(float(self.time_left))

    @property
    def date_confirm_datetime(self):
        return self.__convert_to_datetime(float(self.date_confirm))
