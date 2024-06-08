import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils.deep_linking import decode_payload
from aiogram.filters import CommandStart, CommandObject
from aiogram.filters.command import Command
from aiogram.utils.deep_linking import create_start_link
from aiogram.methods.get_chat_member import GetChatMember
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from mangodm import connect_to_mongo, Document

from typing import List, Optional

from datetime import datetime, timedelta

import random

import traceback

import text_data as td


MONGODB_CONNECTION_URL = "mongodb://tg_coin_mongo_db_1"
DATABASE_NAME = "test_database"


class User(Document):
    tg_id: int

    balance: int = 0
    state_balance: int = 0

    invite_by: Optional['User'] = None
    referrals_ids: List[str] = []

    last_reward: Optional[datetime] = None
    last_reward_id: Optional[int] = None

    wallet_id: Optional[str] = None

    is_ambassador: bool = False

    class Config:
        collection_name = "Game_Users"


User.register_collection()


CHANEL_ID = '@fgjhgjkhkljl'
CHANEL_LINK = 'https://t.me/fgjhgjkhkljl'
AMBASSADOR_CHAT = "https://t.me/+JRKQV_MyMf8yM2Iy"


REWARD_SECONDS_DELTA = 60 * 60 * 24
REWARDS_CNT = [1, 2, 4, 8, 10]

bot = Bot(token="7151259279:AAGLzcG1lC7ZsDmyR_A2OLLQA-pfDM1Um28")

dp = Dispatcher()



MenuBuilder = ReplyKeyboardBuilder()
MenuBuilder.row(
    KeyboardButton(text="📖 Инструкция"),
    KeyboardButton(text="💰 Баланс")
)
MenuBuilder.row(
    KeyboardButton(text="👛 Привязать кошелек"),
    KeyboardButton(text="🤑 Ежедневный бонус")
)
MenuBuilder.row(
    KeyboardButton(text="🎲 Игра 48/52"),
    KeyboardButton(text="💎 Амбассадор")
)
MenuKeyboard = MenuBuilder.as_markup(resize_keyboard=True)


EN_MenuBuilder = ReplyKeyboardBuilder()
EN_MenuBuilder.row(
    KeyboardButton(text="📖 Instruction"),
    KeyboardButton(text="💰 Balance")
)
EN_MenuBuilder.row(
    KeyboardButton(text="👛 Link wallet"),
    KeyboardButton(text="🤑 Daily bonus")
)
EN_MenuBuilder.row(
    KeyboardButton(text="🎲 Game 48/52"),
    KeyboardButton(text="💎 Ambassador")
)
EN_MenuBuilder = EN_MenuBuilder.as_markup(resize_keyboard=True)


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

async def add_balance(user: User, add_cnt: int, reson: str):
    user.balance += add_cnt

    resons_for_state = ["reward", "invite"]

    if reson in resons_for_state:
        user.state_balance += add_cnt

        if user.invite_by and user.invite_by.is_ambassador:
            await add_balance(ser.invite_by, int((add_cnt / 100) * 10), "ambassador")

    await user.update()


def get_lg(user):
    if user.language_code == "ru":
        return "ru"
    else:
        return "en"


async def request_subscribe(callback):
    LG = get_lg(callback.from_user)
    try:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(
            text=td.SUB_REQ["chanel_btn"][LG],
            url=CHANEL_LINK)
        )
        builder.row(InlineKeyboardButton(
            text=td.SUB_REQ["check_sub_btn"][LG],
            callback_data='check_sub')
        )


        await callback.answer(td.SUB_REQ["need_sub_to_continue"][LG], reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())


@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: types.CallbackQuery):
    try:
        LG = get_lg(callback.from_user)
        user_channel_status = await bot.get_chat_member(chat_id=CHANEL_ID, user_id=callback.from_user.id)
        if user_channel_status.status != 'left':
            await callback.answer(td.SUB_REQ["ok_sub"][LG], parse_mode="HTML")
            await callback.message.delete()
        else:
            await callback.answer(td.SUB_REQ["no_sub"][LG], parse_mode="HTML")
    except Exception as e:
        pritn(str(e))


@dp.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject):
    try:
        if not (await is_sub(message.from_user.id)):
            await request_subscribe(message)
        LG = get_lg(message.from_user)
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

                    await add_balance(inviter_user, 100, "invite")
                except Exception as e:
                    print(traceback.format_exc())
            else:
                user = User(tg_id=message.from_user.id)
                await user.create()

        await message.answer(td.START["hello"][LG].format(user_name=message.from_user.first_name), parse_mode="HTML")

        await message.answer(td.START["menu"][LG], reply_markup=MenuKeyboard if LG == "ru" else EN_MenuBuilder, parse_mode="HTML")
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())



@dp.message(F.text == "📖 Instruction")
@dp.message(F.text == "📖 Инструкция")
async def terms(message: types.Message):
    try:
        LG = get_lg(message.from_user)
        user = await User.get(tg_id=message.from_user.id)
        invite_link = await create_start_link(bot, f'invite_{user.id}')

        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text=td.INVITE["btn"][LG],
            switch_inline_query=td.INVITE["invite"][LG].format(invite_link=invite_link))
        )
        await message.answer(td.INSTRUCTION["instruction"][LG].format(channel_link=CHANEL_LINK, invite_link=invite_link), reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())


@dp.message(F.text == "💰 Баланс")
@dp.message(F.text == "💰 Balance")
async def balance(message: types.Message):
    try:
        if not (await is_sub(message.from_user.id)):
            await request_subscribe(message)
            return

        LG = get_lg(message.from_user)
        user = await User.get(tg_id=message.from_user.id)
        invite_link = await create_start_link(bot, f'invite_{user.id}')

        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text=td.INVITE["btn"][LG],
            switch_inline_query=td.INVITE["invite"][LG].format(invite_link=invite_link))
        )
        ref_col = len(user.referrals_ids)
        await message.answer(td.BALANCE["balance"][LG].format(user_balance=user.balance, ref_cnt=ref_col), reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())


@dp.message(F.text == "👛 Привязать кошелек")
@dp.message(F.text == "👛 Link wallet")
async def connect_wallet(message: types.Message, state: FSMContext):
    if not (await is_sub(message.from_user.id)):
        await request_subscribe(message)
        return

    LG = get_lg(message.from_user)
    await state.set_state(WalletForm.wallet_id)
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=td.WALLET["cancel_btn"][LG]))

    mkkb = builder.as_markup()
    mkkb.resize_keyboard = True
    mkkb.is_persistent = True

    await message.answer(td.WALLET["instruction"][LG], reply_markup=mkkb, parse_mode="HTML")


@dp.message(F.text == "Отмена")
@dp.message(F.text == "Cancel")
async def cancel_handler(message: types.Message, state: FSMContext):
    """Allow user to cancel action via /cancel command"""
    LG = get_lg(message.from_user)
    current_state = await state.get_state()
    if current_state is None:
        return

    # Cancel state and inform user about it
    await state.clear()
    await message.answer(td.WALLET["canceled"][LG], reply_markup=MenuKeyboard if LG == "ru" else EN_MenuBuilder, parse_mode="HTML")


@dp.message(WalletForm.wallet_id)
async def process_name(message: types.Message, state: FSMContext):
    LG = get_lg(message.from_user)

    await state.clear()

    user = await User.get(tg_id=message.from_user.id)
    user.wallet_id = message.text
    await user.update()

    await message.answer(td.WALLET["okay"][LG], reply_markup=MenuKeyboard if LG == "ru" else EN_MenuBuilder, parse_mode="HTML")


@dp.message(F.text == "🤑 Ежедневный бонус")
@dp.message(F.text == "🤑 Daily bonus")
async def reward(message: types.Message):
    try:
        if not (await is_sub(message.from_user.id)):
            await request_subscribe(message)
            return
        LG = get_lg(message.from_user)
        user = await User.get(tg_id=message.from_user.id)

        if len(user.referrals_ids) < 2:
            invite_link = await create_start_link(bot, f'invite_{user.id}')
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(
                text=td.INVITE["btn"][LG],
                switch_inline_query=td.INVITE["invite"][LG].format(invite_link=invite_link))
            )
            await message.answer(td.REWARD["invite_2"][LG], parse_mode="HTML", reply_markup=builder.as_markup())
            return

        
        date_delta = None
        if user.last_reward is not None:
            date_delta = datetime.now() - user.last_reward

        if date_delta is None or (date_delta.days >= 1):
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(
                text=td.REWARD["get_btn"][LG],
                callback_data='get_reward')
            )
            await message.answer(td.REWARD["can_get"][LG], reply_markup=builder.as_markup(), parse_mode="HTML")

        else:
            now_date = datetime.now()
            next_date = now_date + timedelta(days=1)
            next_date = next_date.replace(hour=0, minute=0, second=0, microsecond=0)

            time_until_reward = next_date - now_date
            hours_until_reward = time_until_reward.seconds // 3600
            minutes_until_reward = (time_until_reward.seconds // 60) % 60
            await message.answer(td.REWARD["when_can"][LG].format(hours=hours_until_reward, minutes=minutes_until_reward), parse_mode="HTML")
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())


@dp.callback_query(F.data == "get_reward")
async def get_reward(callback: types.CallbackQuery):
    try:
        LG = get_lg(callback.from_user)
        user = await User.get(tg_id=callback.from_user.id)
        if user.last_reward is None or (user.last_reward + timedelta(seconds=REWARD_SECONDS_DELTA) < datetime.now()):
            add_cnt = 0
            if user.last_reward_id is None:
                add_cnt = REWARDS_CNT[0]
                user.last_reward_id = 0
            else:
                date_delta = datetime.now() - user.last_reward
                if date_delta.days >= 2:
                    add_cnt = REWARDS_CNT[0]
                    user.last_reward_id = 0
                else:
                    if user.last_reward_id == len(REWARDS_CNT) - 1:
                        add_cnt = REWARDS_CNT[0]
                        user.last_reward_id = 0
                    else:
                        add_cnt = REWARDS_CNT[user.last_reward_id + 1]
                        user.last_reward_id += 1

            await add_balance(user, add_cnt, "reward")
            
            user.last_reward = datetime.now()
            await user.update()
            
            await callback.message.delete()
            await callback.message.answer(td.REWARD["received"][LG].format(bonus_cnt=add_cnt), parse_mode="HTML")
        else:
            await callback.answer(td.REWARD["cant_get"][LG], parse_mode="HTML")
    except Exception as e:
        pritn(str(e))
        print(traceback.format_exc())


async def start_game(message, show_rule=True):
    LG = get_lg(message.from_user)

    if show_rule:
        await message.answer(td.GAME["instruction"][LG], parse_mode="HTML")
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="1 STN",
            callback_data='bet_1'
        ),
        InlineKeyboardButton(
            text="2 STN",
            callback_data='bet_2'
        ),
        InlineKeyboardButton(
            text="4 STN",
            callback_data='bet_4'
        ),
        InlineKeyboardButton(
            text="8 STN",
            callback_data='bet_8'
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="15 STN",
            callback_data='bet_15'
        ),
        InlineKeyboardButton(
            text="30 STN",
            callback_data='bet_30'
        ),
        InlineKeyboardButton(
            text="60 STN",
            callback_data='bet_60'
        ),
        InlineKeyboardButton(
            text="100 STN",
            callback_data='bet_100'
        )
    )
    await message.answer(td.GAME["bet"][LG], reply_markup=builder.as_markup(), parse_mode="HTML")


@dp.message(F.text == "🎲 Игра 48/52")
@dp.message(F.text == "🎲 Game 48/52")
async def game(message: types.Message):
    if not (await is_sub(message.from_user.id)):
        await request_subscribe(message)
        return
    try:
        ikb_donate = InlineKeyboardMarkup(row_width=1,
                                    inline_keyboard=[
                                        [
                                            InlineKeyboardButton(text='game', web_app=WebAppInfo(url=f'https://3937-46-39-56-187.ngrok-free.app'))
                                        ]
                                    ])

        await message.answer("запустить угру", reply_markup=ikb_donate)
    except Exception as e:
        pritn(str(e))
        print(traceback.format_exc())


# @dp.message(F.text == "🎲 Игра 48/52")
# @dp.message(F.text == "🎲 Game 48/52")
# async def game(message: types.Message):
#     if not (await is_sub(message.from_user.id)):
#         await request_subscribe(message)
#         return
#     await start_game(message)

@dp.callback_query(F.data == "game_again")
async def game_again(callback: types.CallbackQuery):
    await start_game(callback.message, show_rule=False)


async def get_bet(callback: types.CallbackQuery, bet: int):
    try:
        LG = get_lg(callback.from_user)

        user = await User.get(tg_id=callback.from_user.id)

        if user.balance < bet:
            await callback.message.answer(td.GAME["less_tokens"][LG], parse_mode="HTML")
            return

        GAMES[callback.from_user.id] = GameState()
        GAMES[callback.from_user.id].bet = bet

        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="< 48",
            callback_data='game_48')
        )
        builder.add(InlineKeyboardButton(
            text="> 52",
            callback_data='game_52')
        )

        await callback.message.answer(td.GAME["num"][LG], reply_markup=builder.as_markup(), parse_mode="HTML")
    except Exception as e:
        pritn(str(e))
        print(traceback.format_exc())


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

@dp.callback_query(F.data == "bet_15")
async def get_bet_8(callback: types.CallbackQuery):
    await get_bet(callback, 15)

@dp.callback_query(F.data == "bet_30")
async def get_bet_8(callback: types.CallbackQuery):
    await get_bet(callback, 30)

@dp.callback_query(F.data == "bet_60")
async def get_bet_8(callback: types.CallbackQuery):
    await get_bet(callback, 60)

@dp.callback_query(F.data == "bet_100")
async def get_bet_8(callback: types.CallbackQuery):
    await get_bet(callback, 100)


async def game_bet(callback: types.CallbackQuery, num: int):
    LG = get_lg(callback.from_user)

    user = await User.get(tg_id=callback.from_user.id)
    bot_num = random.randint(1, 100)
    random_number = random.uniform(0, 100)
    bot_num = round(random_number, 2)


    await callback.message.answer(td.GAME["bot_num"][LG].format(bot_num=bot_num), parse_mode="HTML")

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text=td.GAME["again"][LG],
        callback_data='game_again')
    )

    if num == 48:
        if bot_num < 48:
            await add_balance(user, GAMES[callback.from_user.id].bet, "game")
            await callback.message.answer("You win!", reply_markup=builder.as_markup(), parse_mode="HTML")
        else:
            await add_balance(user, -(GAMES[callback.from_user.id].bet), "game")
            await callback.message.answer("You lose!", reply_markup=builder.as_markup(), parse_mode="HTML")
    if num == 52:
        if bot_num > 52:
            await add_balance(user, GAMES[callback.from_user.id].bet, "game")
            await callback.message.answer("You win!", reply_markup=builder.as_markup(), parse_mode="HTML")
        else:
            await add_balance(user, -(GAMES[callback.from_user.id].bet), "game")
            await callback.message.answer("You lose!", reply_markup=builder.as_markup(), parse_mode="HTML")

    del GAMES[callback.from_user.id]


@dp.callback_query(F.data == "game_48")
async def game_bet_48(callback: types.CallbackQuery):
    await game_bet(callback, 48)

@dp.callback_query(F.data == "game_52")
async def game_bet_52(callback: types.CallbackQuery):
    await game_bet(callback, 52)


@dp.message(F.text == "💎 Амбассадор")
@dp.message(F.text == "💎 Ambassador")
async def ambassador(message: types.Message):
    if not (await is_sub(message.from_user.id)):
        await request_subscribe(message)
        return

    LG = get_lg(message.from_user)

    user = await User.get(tg_id=message.from_user.id)

    if len(user.referrals_ids) < 100:
        await message.answer(td.AMBASSADOR["cant"][LG], parse_mode="HTML")
    else:
        if user.is_ambassador:
            await message.answer(td.AMBASSADOR["already"][LG].format(AMBASSADOR_CHAT=AMBASSADOR_CHAT), parse_mode="HTML")
        else:
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(
                text=td.AMBASSADOR["be_amb_btn"][LG],
                callback_data="be_ambassador")
            )
            await message.answer(td.AMBASSADOR["be_amb_msg"][LG], reply_markup=builder.as_markup(), parse_mode="HTML")


@dp.callback_query(F.data == "be_ambassador")
async def be_ambassador(callback: types.CallbackQuery):
    try:
        LG = get_lg(callback.from_user)

        user = await User.get(tg_id=callback.from_user.id)
        if user.is_ambassador:
            return

        user.is_ambassador = True
        await user.update()


        add_cnt = 0
        for ref_id in user.referrals_ids:
            ref = await User.get(id=ref_id)
            if ref:
                add_cnt += int((ref.state_balance / 100) * 10)

        await callback.message.answer(td.AMBASSADOR["stay_amb"][LG].format(cnt=add_cnt, AMBASSADOR_CHAT=AMBASSADOR_CHAT), parse_mode="HTML")

        await add_balance(user, add_cnt, "ambassador")
    except Exception as e:
        pritn(str(e))
        print(traceback.format_exc())

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
