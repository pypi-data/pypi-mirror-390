from __future__ import annotations

from typing import Optional, Union

from pydantic import BaseModel

from .error import ErrorMessage


class LinkInfoError(BaseModel):
    link: str
    error: ErrorMessage


class LinkInfo(BaseModel):
    link: str
    filename: str
    size: int
    host: str
    hostDomain: str


class LinkInfos(BaseModel):
    infos: list[Union[LinkInfo, LinkInfoError]]


class LinkRedirect(BaseModel):
    links: list[str]


class LinkUnlockStream(BaseModel):
    id: str
    ext: str
    quality: str
    filesize: int
    name: str
    proto: Optional[str]
    link: Optional[str]


class LinkUnlock(BaseModel):
    id: str
    filename: str
    host: str
    hostDomain: Optional[str] = None
    filesize: int
    link: Optional[str] = None
    streams: Optional[list[LinkUnlockStream]] = None
    delayed: Optional[str] = None


class LinkStream(BaseModel):
    link: str
    filename: str
    filesize: int
    delayed: Optional[int]


class LinkDelayed(BaseModel):
    status: int
    time_left: int
    link: Optional[str]
