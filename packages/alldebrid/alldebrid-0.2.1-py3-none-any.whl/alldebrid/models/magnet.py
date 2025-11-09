import itertools
from typing import Annotated, Any, Iterable, Optional, Union

from pydantic import BaseModel, BeforeValidator

from .error import ErrorMessage


class MagnetErrorURI(BaseModel):
    magnet: str
    error: ErrorMessage


class MagnetErrorFile(BaseModel):
    file: str
    error: ErrorMessage


class MagnetUploadURI(BaseModel):
    magnet: str
    name: str
    id: int
    hash: str
    size: int
    ready: bool


class MagnetUploadFile(BaseModel):
    file: str
    name: str
    id: int
    hash: str
    size: int
    ready: bool


class MagnetInstantURI(BaseModel):
    magnet: str
    hash: str
    instant: bool


class MagnetLinkEntryNormal(BaseModel):
    path: str
    fname: str
    size: int


class MagnetLinkEntry(BaseModel):
    n: str
    e: Optional[list["MagnetLinkEntry"]] = None
    s: Optional[int] = None

    @classmethod
    def parse(cls, v: dict[str, Any]):
        if "e" not in v:
            return MagnetLinkEntry(**v)
        v["e"] = [cls.parse(f) for f in v["e"]]
        return MagnetLinkEntry(**v)

    def walk(self, path: str) -> Iterable[MagnetLinkEntryNormal]:
        if self.e is not None:
            for entry in self.e:
                yield from entry.walk(path + self.n + "/")
        else:
            yield MagnetLinkEntryNormal(path=path, fname=self.n, size=self.s or 0)


class MagnetLink(BaseModel):
    @staticmethod
    def parse_files(x: list[Any]):
        return list(itertools.chain(*(MagnetLinkEntry.parse(f).walk("") for f in x)))

    link: str
    filename: str
    size: int
    files: Annotated[list[MagnetLinkEntryNormal], BeforeValidator(parse_files)]


class MagnetStatus(BaseModel):
    id: int
    filename: str
    size: int
    hash: str
    status: str
    statusCode: int
    downloaded: int
    uploaded: int
    seeders: int
    downloadSpeed: int
    uploadSpeed: int
    uploadDate: int
    completionDate: int
    links: list[MagnetLink]
    type: str
    notified: bool
    version: int


class MagnetUploadFiles(BaseModel):
    files: list[Union[MagnetUploadFile, MagnetErrorFile]]


class MagnetUploadURIs(BaseModel):
    magnets: list[Union[MagnetUploadURI, MagnetErrorURI]]


class MagnetInstants(BaseModel):
    magnets: list[Union[MagnetInstantURI, MagnetErrorURI]]


class MagnetStatusesList(BaseModel):
    magnets: list[MagnetStatus]


class MagnetStatusesDict(BaseModel):
    magnets: dict[str, MagnetStatus]


class MagnetStatusesOne(BaseModel):
    magnets: MagnetStatus


MagnetStatuses = MagnetStatusesDict | MagnetStatusesList | MagnetStatusesOne
