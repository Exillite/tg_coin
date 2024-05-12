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

from datetime import datetime, timedelta

import random

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

REWARD_SECONDS_DELTA = 30 


bot = Bot(token="7151259279:AAGLzcG1lC7ZsDmyR_A2OLLQA-pfDM1Um28")

dp = Dispatcher()



MenuBuilder = ReplyKeyboardBuilder()
MenuBuilder.row(
    KeyboardButton(text="Инструкция"),
    KeyboardButton(text="Баланс")
)
MenuBuilder.row(
    KeyboardButton(text="Привязать кошелёк"),
    KeyboardButton(text="Ежедневный бонус")
)
MenuBuilder.row(
    KeyboardButton(text="Игра"),
    KeyboardButton(text="Амбассадор")
)
MenuBuilder.row(KeyboardButton(text="Пригласить друга"))



class WalletForm(StatesGroup):
    wallet_id = State()

class GameState():
    num: int = 0
    bet: int = 0

GAMES = {} # key: tg id, value: GameState

async def is_sub(user_id):
    user_channel_status = await bot.get_chat_member(chat_id=CHANEL_ID, user_id=user_id)
    if user_channel_status.status != 'left':
        return True
    else:
        return False

async def add_balance(user: User, add_cnt: int):
    user.balance += add_cnt
    await user.update()


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


        await message.answer("Меню", reply_markup=MenuBuilder.as_markup())
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
async def connect_wallet(message: types.Message, state: FSMContext):
    await state.set_state(WalletForm.wallet_id)
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Отмена"))

    mkkb = builder.as_markup()
    mkkb.resize_keyboard = True
    mkkb.is_persistent = True

    await message.answer("Отправте ID кошелька в сети TON:", reply_markup=mkkb)


@dp.message(F.text == "Отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    """Allow user to cancel action via /cancel command"""

    current_state = await state.get_state()
    if current_state is None:
        return

    # Cancel state and inform user about it
    await state.clear()
    await message.answer('Отменено.', reply_markup=MenuBuilder.as_markup())


@dp.message(WalletForm.wallet_id)
async def process_name(message: types.Message, state: FSMContext):

    await state.clear()

    user = await User.get(tg_id=message.from_user.id)
    user.wallet_id = message.text
    await user.update()

    await message.answer(f"Кошелёк привязан.", reply_markup=MenuBuilder.as_markup())


@dp.message(F.text == "Ежедневный бонус")
async def reward(message: types.Message):
    try:
        user = await User.get(tg_id=message.from_user.id)

        if user.last_reward is None or (user.last_reward + timedelta(seconds=REWARD_SECONDS_DELTA) < datetime.now()):
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(
                text="Забрать бонус",
                callback_data='get_reward')
            )
            await message.answer(f"Вы можете забрать бонус.", reply_markup=builder.as_markup())

        else:
            time_until_reward = (user.last_reward + timedelta(seconds=REWARD_SECONDS_DELTA)) - datetime.now()
            hours_until_reward = time_until_reward.seconds // 3600
            minutes_until_reward = (time_until_reward.seconds // 60) % 60
            await message.answer("Ежедневный бонус будет доступен через {} часов и {} минут.".format(hours_until_reward, minutes_until_reward))
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())


@dp.callback_query(F.data == "get_reward")
async def get_reward(callback: types.CallbackQuery):
    try:
        user = await User.get(tg_id=callback.from_user.id)
        if user.last_reward is None or (user.last_reward + timedelta(seconds=REWARD_SECONDS_DELTA) < datetime.now()):
            await add_balance(user, 100)
            
            user.last_reward = datetime.now()
            await user.update()
            
            await callback.message.delete()
            await callback.message.answer("Вы получили ежедневный бонус.")
        else:
            await callback.answer("Ежедневный бонус пока не доступен.")
    except Exception as e:
        pritn(str(e))
        print(traceback.format_exc())


@dp.message(F.text == "Ежедневный бонус")
async def reward(message: types.Message):
    await message.answer("Добро пожаловать в игру '48/52'!\nВыберите вашу ставку: 1, 2, 4 или 8 STN (Superton).\nПосле выбора ставки, угадайте, будет ли выпавшее случайное число больше 52 или меньше 48.\nЕсли ваш выбор совпадает с результатом, вы побеждаете и получаете выигрыш в размере вашей ставки.\nПомните, что число 48 для <48 считается проигрышным, а 47,99 - выигрышным. То же самое с числом 52.")
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="1 STN",
        callback_data='bet_1')
    )
    builder.add(InlineKeyboardButton(
        text="2 STN",
        callback_data='bet_2')
    )
    builder.add(InlineKeyboardButton(
        text="4 STN",
        callback_data='bet_4')
    )
    builder.add(InlineKeyboardButton(
        text="8 STN",
        callback_data='bet_8')
    )
    await message.answer("Выберите ставку:", reply_markup=builder.as_markup())



async def get_bet(callback: types.CallbackQuery, bet: int):
    user = await User.get(tg_id=callback.from_user.id)

    if user.balance < bet:
        callback.message.answer("У вас недостаточно средств")
        return

    GAMES[callback.from_user.id] = GameState()
    GAMES[callback.from_user.id].bet = bet

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Меньше 48",
        callback_data='game_48')
    )
    builder.add(InlineKeyboardButton(
        text="Больше 52",
        callback_data='game_52')
    )

    await callback.message.answer("Угадайте число", reply_markup=builder.as_markup())


@dp.callback_query(F.data == "bet_1")
async def get_bet_1(callback: types.CallbackQuery):
    await get_bet(callback, 1)

@dp.callback_query(F.data == "bet_2")
async def get_bet_2(callback: types.CallbackQuery):
    await get_bet(callback, 2)

@dp.callback_query(F.data == "bet_4")
async def get_bet_4(callback: types.CallbackQuery):
    await get_bet(callback, 4)

@dp.callback_query(F.data == "bet_8")
async def get_bet_8(callback: types.CallbackQuery):
    await get_bet(callback, 8)


async def game_bet(callback: types.CallbackQuery, num: int):
    user = await User.get(tg_id=callback.from_user.id)
    bot_num = random.randint(1, 100)

    if num == 48:
        if bot_num < 48:
            add_balance(user, GAMES[callback.from_user.id].bet)
            await callback.message.answer("You win!")
        else:
            add_balance(user, -(GAMES[callback.from_user.id].bet))
            await callback.message.answer("You lose!")
    if num == 52:
        if bot_num > 52:
            add_balance(user, GAMES[callback.from_user.id].bet)
            await callback.message.answer("You win!")
        else:
            add_balance(user, -(GAMES[callback.from_user.id].bet))
            await callback.message.answer("You lose!")

    del GAMES[callback.from_user.id]


@dp.callback_query(F.data == "game_48")
async def game_bet_48(callback: types.CallbackQuery):
    await game_bet(callback, 48)

@dp.callback_query(F.data == "game_52")
async def game_bet_52(callback: types.CallbackQuery):
    await game_bet(callback, 52)


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
