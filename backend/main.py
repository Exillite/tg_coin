from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from contextlib import asynccontextmanager

from mangodm import connect_to_mongo, close_mongo_connection

from models import User, Boost, Upgrade
from schemas import *

import datetime
import time


MONGODB_CONNECTION_URL = "mongodb://tg_cliker_coin_mongo_db_1"
DATABASE_NAME = "test_database"


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # execute when app is loading
    time.sleep(10)
    print("Loading app")
    await connect_to_mongo(MONGODB_CONNECTION_URL, DATABASE_NAME)
    print("Connected to mongo")
    yield
    # execute when app is shutting down
    print("Close db connection")
    close_mongo_connection()


app = FastAPI(lifespan=app_lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


RANGS = [
    "wood",
    "bronze",
    "silver",
    "gold",
    "platina",
    "diamond",
    "kryptonite"
]

RANGS_FROM = {
    RANGS[0]: 0,
    RANGS[1]: 10000,
    RANGS[2]: 100000,
    RANGS[3]: 500000,
    RANGS[4]: 1000000,
    RANGS[5]: 10000000,
    RANGS[6]: 50000000,
}

GIVE_FOR_RANG = {
    RANGS[0]: 0,
    RANGS[1]: 5000,
    RANGS[2]: 20000,
    RANGS[3]: 20000,
    RANGS[4]: 100000,
    RANGS[5]: 300000,
    RANGS[6]: 1000000,
}

GIVE_INVITER_FOR_RANG = {
    RANGS[0]: 0,
    RANGS[1]: 5000,
    RANGS[2]: 20000,
    RANGS[3]: 20000,
    RANGS[4]: 100000,
    RANGS[5]: 300000,
    RANGS[6]: 1000000,
}


RANGS_TASKS = [
    {"task_type": "rang", "title": "Bronze", "cnt": 5000, "info": "bronze"},
    {"task_type": "rang", "title": "Silver", "cnt": 20000, "info": "silver"},
    {"task_type": "rang", "title": "Gold", "cnt": 20000, "info": "gold"},
    {"task_type": "rang", "title": "Platina", "cnt": 100000, "info": "platina"},
    {"task_type": "rang", "title": "Diamond", "cnt": 300000, "info": "diamond"},
    {"task_type": "rang", "title": "Kryptonite", "cnt": 1000000, "info": "kryptonite"},
]


def get_rang(balance: int):
    rang = "none"
    for key, value in RANGS_FROM.items():
        if balance >= value:
            rang = key

    return rang

def how_many_for_friend(rang: str):
    rang_id = RANGS.index(rang)
    cnt = 0
    for i in range(rang_id + 1):
        cnt += GIVE_INVITER_FOR_RANG[RANGS[i]]
    return cnt


@app.post("/api/connect")
async def connect(connect_data: NewConnectData):
    u = await User.get(tg_id=connect_data.tg_id)

    if u:
        return u.to_response()

    new_u = User(
        tg_id=connect_data.tg_id,
        nick=connect_data.nick,
        balance=0, click_add=1,
        free_try=3,
        rang=RANGS[0],
        last_session=datetime.datetime.now(),
        can_next_session_after=datetime.datetime.now(),
        session_time=30,
        tasks=RANGS_TASKS)

    await new_u.create()

    if connect_data.friend_id:
        print("!!!!!!!!", connect_data.friend_id)
        fr = await User.get(id=connect_data.friend_id)
        fr.friends.append(new_u.id)
        await fr.update()

        new_u.inviter = connect_data.friend_id
        await new_u.update()


    return new_u.to_response()


@app.post("/api/get_friends")
async def get_friends(data: ConnectData):
    u = await User.get(tg_id=data.tg_id)
    ret = []
    for fr in u.friends:
        fd = await User.get(id=fr)
        if fd:
            ret.append(fd.to_response())
            ret[-1]["for_invite"] = how_many_for_friend(fd.rang)

    return {"friends": ret}


@app.post("/api/save_session")
async def save_session(data: SaveSessionData):
    u = await User.get(tg_id=data.tg_id)
    if not u:
        return "Error"
    u.last_session = datetime.datetime.now()

    if u.free_try > 0:
        u.can_next_session_after = datetime.datetime.now()
        u.free_try -= 1
    else:
        u.can_next_session_after = datetime.datetime.now() + datetime.timedelta(seconds=30)
        u.free_try = 3
    
    u.balance = data.balance


    new_rang = get_rang(u.balance)
    if new_rang != u.rang:
        u.rang = new_rang

        inviter = await User.get(id=u.inviter)
        if inviter:
            inviter.balance += GIVE_INVITER_FOR_RANG[new_rang]
            await inviter.update()

    await u.update()

    return u.to_response()


@app.post("/api/time_to_session")
async def time_to_session(data: ConnectData):
    u = await User.get(tg_id=data.tg_id)
    tts = (u.can_next_session_after - datetime.datetime.now()).total_seconds()
    if tts < 0:
        tts =  0
    return {"tts": tts}


# @app.put("/api/clicks")
# async def clicks(clicks_data: ClicksData):
#     u = await User.get(tg_id=clicks_data.tg_id)
#     if not u:
#         return "Error"

#     u.balance += clicks_data.cnt


@app.post("/api/claim_task")
async def claim_task(data: ClaimData):
    u = await User.get(tg_id=data.tg_id)

    for i in range(len(u.tasks)):
        if u.tasks[i]["info"] == data.task_info:
            u.balance += u.tasks[i]["cnt"]
            u.tasks.pop(i)
            break

    new_rang = get_rang(u.balance)
    if new_rang != u.rang:
        u.rang = new_rang

        inviter = await User.get(id=u.inviter)
        if inviter:
            inviter.balance += GIVE_INVITER_FOR_RANG[new_rang]
            await inviter.update()

    await u.update()

    return u.to_response()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
