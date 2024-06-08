from mangodm import Document
from typing import List, Optional
from datetime import datetime


class Boost(Document):
    boost_type: str
    data: Optional[dict]

    class Config:
        collection_name = "Boosts"


class Upgrade(Document):
    upgrade_type: str
    data: Optional[dict]

    class Config:
        collection_name = "Upgrades"


class User(Document):
    tg_id: int
    nick: str

    balance: int
    click_add: int
    rang: str

    boosts: List[Boost] = []
    upgrades: List[Upgrade] = []
    tasks: List[dict] = [] # {task_type: str, title: str, cnt: int, info: str}

    free_try: int
    last_session: datetime
    can_next_session_after: datetime
    session_time: int  # in seconds

    friends: List[str] = []
    inviter: Optional[str] = None

    class Config:
        collection_name = "Users"


Boost.register_collection()
Upgrade.register_collection()
User.register_collection()
