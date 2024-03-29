import logging
import urllib.parse
from typing import Optional, Union

import aiohttp

from kwork_api_client.exceptions import KworkException
from kwork_api_client.types import *
from kwork_api_client.types.all import *

logger = logging.getLogger(__name__)


class Kwork:
    def __init__(
        self,
        login: str,
        password: str,
        proxy: typing.Optional[str] = None,
        phone_last: typing.Optional[str] = None,
    ):
        connector: typing.Optional[aiohttp.BaseConnector] = None

        if proxy is not None:
            try:
                from aiohttp_socks import ProxyConnector
            except ImportError:
                raise ImportError(
                    "You have to install aiohttp_socks for using"
                    " proxy, make it by pip install aiohttp_socks"
                )
            connector = ProxyConnector.from_url(proxy)

        self.session = aiohttp.ClientSession(connector=connector)
        self.host = "https://api.kwork.ru/{}"
        self.login = login
        self.password = password
        self._token: typing.Optional[str] = None
        self.phone_last = phone_last

    @property
    async def token(self) -> str:
        if self._token is None:
            self._token = await self.get_token()
        return self._token

    async def api_request(
        self, method: str, api_method: str, **params
    ) -> typing.Union[dict, typing.NoReturn]:
        params = {k: v for k, v in params.items() if v is not None}
        logging.debug(
            f"making {method} request on /{api_method} with params - {params}"
        )
        async with self.session.request(
            method=method,
            url=self.host.format(api_method),
            headers={"Authorization": "Basic bW9iaWxlX2FwaTpxRnZmUmw3dw=="},
            params=params,
        ) as resp:
            if resp.content_type != "application/json":
                error_text: str = await resp.text()
                raise KworkException(error_text)
            json_response: dict = await resp.json()
            if not json_response["success"]:
                raise KworkException(json_response["error"])
            logging.debug(f"result of request on /{api_method} - {json_response}")
            return json_response

    async def close(self) -> None:
        await self.session.close()

    async def get_token(self) -> str:
        resp: dict = await self.api_request(
            method="post",
            api_method="signIn",
            login=self.login,
            password=self.password,
            phone_last=self.phone_last,
        )
        return resp["response"]["token"]

    async def get_me(self) -> Actor:
        actor = await self.api_request(
            method="post", api_method="actor", token=await self.token
        )
        return Actor(**actor["response"])

    async def get_user(self, user_id: int) -> User:
        """
        :param user_id: you can find it in dialogs
        :return:
        """
        user = await self.api_request(
            method="post", api_method="user", id=user_id, token=await self.token
        )
        return User(**user["response"])

    async def set_typing(self, recipient_id: int) -> dict:
        resp = await self.api_request(
            method="post",
            api_method="typing",
            recipientId=recipient_id,
            token=await self.token,
        )
        return resp

    async def get_all_dialogs(self) -> typing.List[DialogMessage]:
        page = 1
        dialogs: typing.List[DialogMessage] = []

        while True:
            dialogs_page = await self.api_request(
                method="post",
                api_method="dialogs",
                filter="all",
                page=page,
                token=await self.token,
            )
            if not dialogs_page["response"]:
                break

            for dialog in dialogs_page["response"]:
                dialogs.append(DialogMessage(**dialog))
            page += 1

        return dialogs

    async def set_offline(self) -> dict:
        return await self.api_request(
            method="post", api_method="offline", token=await self.token
        )

    async def get_dialog_with_user(self, user_name: str) -> typing.List[InboxMessage]:
        page = 1
        dialog: typing.List[InboxMessage] = []

        while True:
            messages_dict: dict = await self.api_request(
                method="post",
                api_method="inboxes",
                username=user_name,
                page=page,
                token=await self.token,
            )
            if not messages_dict.get("response"):
                break
            for message in messages_dict["response"]:
                dialog.append(InboxMessage(**message))

            if page == messages_dict["paging"]["pages"]:
                break
            page += 1

        return dialog

    async def get_worker_orders(self) -> dict:
        return await self.api_request(
            method="post",
            api_method="workerOrders",
            filter="all",
            token=await self.token,
        )

    async def get_payer_orders(self) -> dict:
        return await self.api_request(
            method="post",
            api_method="payerOrders",
            filter="all",
            token=await self.token,
        )

    async def get_notifications(self) -> dict:
        return await self.api_request(
            method="post",
            api_method="notifications",
            token=await self.token,
        )

    async def get_categories(self) -> typing.List[Category]:
        raw_categories = await self.api_request(
            method="post",
            api_method="categories",
            type="1",
            token=await self.token,
        )
        categories = []
        for dict_category in raw_categories["response"]:
            category = Category(**dict_category)
            categories.append(category)
        return categories

    async def get_connects(self) -> Connects:
        raw_projects = await self.api_request(
            method="post",
            api_method="projects",
            categories="",
            token=await self.token,
        )
        return Connects(**raw_projects["connects"])

    async def get_projects(
        self,
        categories_ids: typing.List[Union[int, str]],
        price_from: Optional[int] = None,
        price_to: Optional[int] = None,
        hiring_from: Optional[int] = None,
        kworks_filter_from: Optional[int] = None,
        kworks_filter_to: Optional[int] = None,
        page: Optional[int] = None,
        query: Optional[str] = None,
    ) -> typing.List[WantWorker]:
        """
        categories_ids - Список ID рубрик через запятую, либо 'all' - для выборки по всем рубрикам.
         С пустым значением делает выборку по любимым рубрикам.
        price_from - Бюджет от (включительно)
        price_to - Бюджет до (включительно)
        hiring_from - Процент найма от
        kworks_filter_from - Количество предложений от (не включительно)
        kworks_filter_to - Количество предложений до (включительно)
        page - Страница выдачи
        query - Поисковая строка
        """

        raw_projects = await self.api_request(
            method="post",
            api_method="projects",
            categories=",".join(str(category) for category in categories_ids),
            price_from=price_from,
            price_to=price_to,
            hiring_from=hiring_from,
            kworks_filter_from=kworks_filter_from,
            kworks_filter_to=kworks_filter_to,
            page=page,
            query=query,
            token=await self.token,
        )
        projects = []
        for dict_project in raw_projects["response"]:
            project = WantWorker(**dict_project)
            projects.append(project)
        return projects

    async def _get_channel(self) -> str:
        channel = await self.api_request(
            method="post", api_method="getChannel", token=await self.token
        )
        return channel["response"]["channel"]

    async def send_message(self, user_id: int, text: str) -> dict:  # noqa
        logging.debug(f"Sending message for {user_id} with text - {text}")
        resp = await self.session.post(
            f"{self.host.format('inboxCreate')}"
            f"?user_id={user_id}"
            f"&text={urllib.parse.quote(text)}&token={await self.token}",
            headers={"Authorization": "Basic bW9iaWxlX2FwaTpxRnZmUmw3dw=="},
        )
        json_resp = await resp.json()
        logging.debug(f"result of sending - {json_resp}")
        return json_resp

    async def delete_message(self, message_id) -> dict:
        return await self.api_request(
            method="post",
            api_method="inboxDelete",
            id=message_id,
            token=await self.token,
        )
