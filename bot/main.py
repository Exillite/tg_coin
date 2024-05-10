import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils.deep_linking import decode_payload
from aiogram.filters import CommandStart, CommandObject
from aiogram.filters.command import Command
from aiogram.utils.deep_linking import create_start_link
from aiogram.methods.get_chat_member import GetChatMember
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram import F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

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

    wallet_id: Optional[str] = None

    class Config:
        collection_name = "Users"

User.register_collection()


CHANEL_ID = '@qwertyuikmnbvcfd'


bot = Bot(token="7151259279:AAGLzcG1lC7ZsDmyR_A2OLLQA-pfDM1Um28")

storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class WalletForm(StatesGroup):
    wallet_id = State()


async def is_sub(user_id):
    user_channel_status = await bot.get_chat_member(chat_id=CHANEL_ID, user_id=user_id)
    if user_channel_status.status != 'left':
        return True
    else:
        return False


async def request_subscribe(callback):
    try:
        # inline_btn_1 = InlineKeyboardButton(text='Подписаться на канал', url='https://t.me/qwertyuikmnbvcfd')
        # inline_btn_2 = InlineKeyboardButton(text='Проверить подписку', callback_data='check_sub')
        # inline_kb = InlineKeyboardMarkup(inline_keyboard=[inline_btn_1, inline_btn_2])

        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text="Подписаться на канал",
            url='https://t.me/qwertyuikmnbvcfd')
        )
        builder.row(InlineKeyboardButton(
            text="Проверить подписку",
            callback_data='check_sub')
        )


        await callback.answer("Для продоления необходимо быть подписанным на канал!", reply_markup=builder.as_markup())
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())


@dp.callback_query(F.data == "check_sub")
async def send_random_value(callback: types.CallbackQuery):
    try:
        user_channel_status = await bot.get_chat_member(chat_id=CHANEL_ID, user_id=callback.from_user.id)
        if user_channel_status.status != 'left':
            await callback.answer("Подписка оформлена.")
            await callback.message.delete()
        else:
            await callback.answer("Вы не подписалис на канал!")
    except Exception as e:
        pritn(str(e))


@dp.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    try:
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

        # invite_link = await create_start_link(bot, f'invite_{user.id}')
        # await message.answer(invite_link)

        builder = ReplyKeyboardBuilder()
        builder.row(
            KeyboardButton(text="Инструкция"),
            KeyboardButton(text="Баланс")
        )
        builder.row(
            KeyboardButton(text="Привязать кошелёк"),
            KeyboardButton(text="Ежедневный бонус")
        )
        builder.row(
            KeyboardButton(text="Игра"),
            KeyboardButton(text="Амбассадор")
        )
        builder.add(KeyboardButton(text="Пригласить друга"))


        await message.answer("Меню", reply_markup=builder.as_markup())
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())



@dp.message(F.text == "Инструкция")
async def terms(message: types.Message):
    await message.answer(
"""
Инструкция:
...

Правила:
...
"""
        )


@dp.message(F.text == "Баланс")
async def balance(message: types.Message):
    user = await User.get(tg_id=message.from_user.id)

    await message.answer(f"Ваш баланс: {user.balance}\nКоличество приглашённых пользователей: {len(user.referrals_ids)}")


@dp.message(F.text == "Привязать кошелёк")
async def connect_wallet(message: types.Message):
    await WalletForm.wallet_id.set()
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Отмена"))

    await message.answer("Отправте ID кошелька в сети TON:", reply_markup=builder.as_markup())


@dp.message(F.text == "Отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    """Allow user to cancel action via /cancel command"""

    current_state = await state.get_state()
    if current_state is None:
        # User is not in any state, ignoring
        return

    # Cancel state and inform user about it
    await state.finish()
    await message.reply('Отменено.')

    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="Инструкция"),
        KeyboardButton(text="Баланс")
    )
    builder.row(
        KeyboardButton(text="Привязать кошелёк"),
        KeyboardButton(text="Ежедневный бонус")
    )
    builder.row(
        KeyboardButton(text="Игра"),
        KeyboardButton(text="Амбассадор")
    )
    builder.add(KeyboardButton(text="Пригласить друга"))

    await message.answer("Меню", reply_markup=builder.as_markup())

@dp.message(WalletForm.wallet_id)
async def process_name(message: types.Message, state: FSMContext):

    # Finish our conversation
    await state.finish()

    user = await User.get(tg_id=message.from_user.id)
    user.wallet_id = message.text

    await message.answer(f"Кошелёк привязан.")

    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="Инструкция"),
        KeyboardButton(text="Баланс")
    )
    builder.row(
        KeyboardButton(text="Привязать кошелёк"),
        KeyboardButton(text="Ежедневный бонус")
    )
    builder.row(
        KeyboardButton(text="Игра"),
        KeyboardButton(text="Амбассадор")
    )
    builder.add(KeyboardButton(text="Пригласить друга"))

    await message.answer("Меню", reply_markup=builder.as_markup())


# @dp.message(Command("check"))
# async def test_sub(message: types.Message):
#     user_channel_status = await bot.get_chat_member(chat_id=CHANEL_ID, user_id=message.from_user.id)
#     if user_channel_status.status != 'left':
#         await message.answer("Yes")
#     else:
#         await request_subscribe(message)


async def main():
    print("Connecting to MongoDB.")
    await connect_to_mongo(MONGODB_CONNECTION_URL, DATABASE_NAME)

    print("Starting bot.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
