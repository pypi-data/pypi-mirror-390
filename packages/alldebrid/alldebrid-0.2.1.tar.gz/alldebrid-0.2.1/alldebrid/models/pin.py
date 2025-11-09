from typing import Optional

from pydantic import BaseModel


class PinGet(BaseModel):
    pin: str
    check: str
    expires_in: int
    user_url: str
    base_url: str
    check_url: str


class PinCheck(BaseModel):
    activated: bool
    expires_in: int
    apikey: Optional[str]
