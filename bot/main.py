import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils.deep_linking import decode_payload
from aiogram.filters import CommandStart, CommandObject
from aiogram.filters.command import Command
from aiogram.utils.deep_linking import create_start_link

from mangodm import connect_to_mongo, Document

from typing import List, Optional

from datetime import datetime

import traceback


MONGODB_CONNECTION_URL = "mongodb://tg_coin_mongo_db_1"
DATABASE_NAME = "test_database"


class User(Document):
    tg_id: int

    balance: int = 0

    invite_by: Optional['User'] = None
    referrals_ids: List[int] = []

    last_reward: Optional[datetime] = None

    class Config:
        collection_name = "Users"

User.register_collection()


bot = Bot(token="7151259279:AAGLzcG1lC7ZsDmyR_A2OLLQA-pfDM1Um28")
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    user = await User.get(tg_id=message.from_user.id)
    if not user:
        args = command.args
        if args:
            inviter_user = await User.get(id=args.split('_')[1])
            user = User(tg_id=message.from_user.id, invite_by=inviter_user)
            await user.create()
            try:
                inviter_user.referrals_ids.append(user.id)
                await inviter_user.update()
            except Exception as e:
                print(traceback.format_exc())
        else:
            user = User(tg_id=message.from_user.id)
            await user.create()

    await message.answer(f"Hello! {message.from_user.first_name}")

    invite_link = await create_start_link(bot, f'invite_{user.id}')
    await message.answer(invite_link)


async def main():
    print("Connecting to MongoDB.")
    await connect_to_mongo(MONGODB_CONNECTION_URL, DATABASE_NAME)

    print("Starting bot.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
