from pydantic import BaseModel
from typing import Optional


class NewConnectData(BaseModel):
    tg_id: int
    nick: str
    friend_id: Optional[str]

class ConnectData(BaseModel):
    tg_id: int

class ClaimData(BaseModel):
    tg_id: int
    task_info: str

class ClicksData(BaseModel):
    tg_id: int
    cnt: int


class SaveSessionData(BaseModel):
    tg_id: int
    balance: int
