import asyncio
import os.path
from typing import Any, ClassVar, Literal, Optional, Type, TypeVar, Union

import httpx

from .models.link import LinkDelayed, LinkInfo, LinkInfos, LinkRedirect, LinkUnlock
from .models.magnet import (
    MagnetInstants,
    MagnetStatuses,
    MagnetStatusesDict,
    MagnetStatusesList,
    MagnetStatusesOne,
    MagnetUploadFiles,
    MagnetUploadURIs,
)
from .models.pin import PinCheck, PinGet
from .response import Response

T = TypeVar("T")


class Client:
    BASE: ClassVar[str] = "https://api.alldebrid.com"

    def __init__(self, apikey: Optional[str] = None, name: Optional[str] = "py.alldebrid"):
        self._apikey = apikey
        self.agent = name

    async def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        async with httpx.AsyncClient(timeout=60 * 3) as client:
            if "params" in kwargs:
                kwargs["params"]["agent"] = self.agent
                kwargs["params"]["apikey"] = self._apikey
            else:
                kwargs["params"] = {"agent": self.agent, "apikey": self._apikey}
            if url.startswith("/"):
                url = self.BASE + url
            return await client.request(method, url=url, **kwargs)

    @staticmethod
    def _parse_obj(type_: Type[Response[T]], response: httpx.Response) -> T:
        try:
            output = type_.model_validate_json(response.text)
        except Exception:
            with open("last_error.json", "w") as f:
                f.write(response.text)
            raise
        return output.unwrap()

    # Pin auth

    async def pin_get(self):
        resp = await self._request("GET", "/v4/pin/get")
        return self._parse_obj(Response[PinGet], resp)

    async def pin_check(self, check: str, pin: str):
        resp = await self._request(
            "GET",
            "/v4/pin/check",
            params=dict(check=check, pin=pin),
        )
        data = self._parse_obj(Response[PinCheck], resp)
        if data.activated:
            self._apikey = data.apikey
        return data

    async def link_info(self, links: list[str], password: str = ""):
        resp = await self._request(
            "GET",
            "/v4/link/infos",
            params={"link[]": links, "password": password},
        )
        data = self._parse_obj(Response[LinkInfos], resp)
        return data

    async def link_redirect(self, link: str):
        resp = await self._request(
            "GET",
            "/v4/link/redirector",
            params=dict(link=link),
        )
        data = self._parse_obj(Response[LinkRedirect], resp)
        return data

    async def link_unlock(self, link: str, password: str = ""):
        resp = await self._request(
            "GET",
            "/v4/link/unlock",
            params=dict(link=link, password=password),
        )
        data = self._parse_obj(Response[LinkUnlock], resp)
        return data

    async def link_stream(self, id_: str, stream: str):
        resp = await self._request(
            "GET",
            "/v4/link/streaming",
            params=dict(id=id_, stream=stream),
        )
        data = self._parse_obj(Response[LinkInfo], resp)
        return data

    async def link_delayed(self, id_: str):
        resp = await self._request(
            "GET",
            "/v4/link/delayed",
            params=dict(id=id_),
        )
        data = self._parse_obj(Response[LinkDelayed], resp)
        return data

    async def link_download(self, link: str, password: str = ""):
        unlock = await self.link_unlock(link, password)
        while not unlock.link and unlock.delayed:
            delayed = await self.link_delayed(unlock.delayed)
            if delayed.link:
                unlock.link = delayed.link
            else:
                await asyncio.sleep(delayed.time_left + 1)

        return unlock

    async def magnet_upload(self, magnets: list[str]):
        resp = await self._request("POST", "/v4/magnet/upload", data={"magnets": magnets})
        return self._parse_obj(Response[MagnetUploadURIs], resp)

    async def magnet_upload_file(self, fnames: list[str]):
        resp = await self._request(
            "POST",
            "/v4/magnet/upload/file",
            files=[
                (
                    "files[]",
                    (
                        os.path.basename(fname),
                        open(fname, "rb"),
                        "application/x-bittorrent",
                    ),
                )
                for fname in fnames
            ],
        )
        return self._parse_obj(Response[MagnetUploadFiles], resp)

    async def magnet_upload_raw(self, *items: tuple[str, bytes]):
        resp = await self._request(
            "POST",
            "/v4/magnet/upload/file",
            files=[
                (
                    "files[]",
                    (
                        os.path.basename(fname),
                        data,
                        "application/x-bittorrent",
                    ),
                )
                for fname, data in items
            ],
        )
        return self._parse_obj(Response[MagnetUploadFiles], resp)

    async def magnet_status(
        self,
        id: Optional[int] = None,
        status: Union[
            Literal["active"],
            Literal["ready"],
            Literal["expired"],
            Literal["error"],
            None,
        ] = None,
    ):
        data: dict[str, Any] = {}
        if id is not None:
            data["id"] = id
        if status is not None:
            data["status"] = status
        resp = await self._request("GET", "/v4/magnet/status", params=data)
        result = self._parse_obj(Response[MagnetStatuses], resp)
        if isinstance(result, MagnetStatusesDict):
            return MagnetStatusesList(magnets=list(result.magnets.values()))
        if isinstance(result, MagnetStatusesOne):
            return MagnetStatusesList(magnets=[result.magnets])
        else:
            return result

    async def magnet_status_live(self, session: int, counter: int):
        pass

    async def magnet_delete(self, id: int):
        data = {"id": id}
        resp = await self._request("GET", "/v4/magnet/delete", params=data)
        return self._parse_obj(Response[dict[str, Any]], resp)

    async def magnet_instant(self, magnets: list[str]):
        resp = await self._request(
            "POST",
            "/v4/magnet/instant",
            data={"magnets[]": magnets},
        )
        return self._parse_obj(Response[MagnetInstants], resp)
