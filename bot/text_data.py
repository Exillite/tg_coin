MENU = {
    "instruction": {"ru": "📖 Инструкция", "en": "📖 Instruction"},
    "balance": {"ru": "💰 Баланс", "en": "💰 Balance"},
    "wallet": {"ru": "👛 Привязать кошелек", "en": "👛 Link wallet"},
    "reward": {"ru": "🤑 Ежедневный бонус", "en": "🤑 Daily bonus"},
    "game": {"ru": "🎲 Игра 48/52", "en": "🎲 48/52 Game"},
    "ambassador": {"ru": "💎 Амбассадор", "en": "💎 Ambassador"},
}


SUB_REQ = {
	"chanel_btn": {"ru": "Подписаться на канал", "en": "Subscribe to channel"},
	"check_sub_btn": {"ru": "Проверить подписку", "en": "Check subscription"},
	"need_sub_to_continue": {"ru": "Для продолжения необходимо быть подписанным на канал!", "en": "Subscription to the channel is required to continue!"},
	"ok_sub": {"ru": "Подписка оформлена.", "en": "Subscription completed."},
	"no_sub": {"ru": "Вы не подписались на канал!", "en": "You are not subscribed to the channel!"},
}

START = {
    "hello": {"ru": "Привет, {user_name}!", "en": "Hello, {user_name}!"},
    "menu": {"ru": "Меню", "en": "Menu"},
}

INVITE = {
    "btn": {"ru": "Пригласить друга", "en": "Invite a friend"},
    "invite": {"ru": "Присоединяйтесь к SUPERTON\n\n{invite_link}", "en": "Join SUPERTON\n\n{invite_link}"},
}

INSTRUCTION = {
    "instruction": {
        "ru": "Хочешь получить <b>AIRDROP</b> токенов <b>$STN?</b>\nТогда нужно:\n1. Быть подписанным на канал ({channel_link})\n2. Пригласить друзей. Чем больше друзей вы пригласите, тем больше ваш заработок.\nПо-настоящему активные участники могут стать Амбассадорами проекта и заработать гораздо больше! 💰💰💰\n\nЗа каждого приведенного друга вы получите: 100 <b>$STN</b>.\n\nПригласить друга\n{invite_link}",
        "en": "Want to get <b>AIRDROP</b> tokens <b>$STN?</b>\nHere's what you need to do:\n1. Subscribe to the channel ({channel_link})\n2. Invite friends. The more friends you invite, the more you earn.\nTruly active participants can become project Ambassadors and earn much more! 💰💰💰\n\nFor each referred friend, you will receive: 100 <b>$STN</b>.\n\nInvite friend\n{invite_link}"
    }
}

BALANCE = {
	"balance": {"ru": "Ваш баланс: <b>{user_balance} $STN</b>.\n\nКоличество приглашённых пользователей: <b>{ref_cnt}</b>", "en": "Your <b>balance: {user_balance} $STR</b>.\n\n Number of invited users: <b>{ref_cnt}</b>"}
}

WALLET = {
    "cancel_btn": {"ru": "Отмена", "en": "Cancel"},
    "instruction": {"ru": "Отправьте адрес некастодиального кошелька в сети TON (рекомендуем Tonkeeper/MyTonWallet/Tonhub):", "en": "Send the address of a non-custodial wallet in the TON network (recommended Tonkeeper/MyTonWallet/Tonhub):"},
    "canceled": {"ru": "Отменено.", "en": "Canceled."},
    "okay": {"ru": "Кошелёк привязан.", "en": "Wallet linked."},
}

REWARD = {
    "invite_2": {"ru": "Пригласите двух друзей, чтобы получать ежедневный бонус", "en": "Invite two friends to receive daily bonus"},
    "get_btn": {"ru": "Забрать бонус", "en": "Claim bonus"},
    "can_get": {"ru": "Вы можете забрать бонус.", "en": "You can claim the bonus."},
    "when_can": {"ru": "Ежедневный бонус будет доступен через {hours} часов и {minutes} минут.", "en": "Daily bonus will be available in {hours} hours and {minutes} minutes."},
    "received": {"ru": "Вы получили ежедневный бонус.", "en": "You have received the daily bonus."},
    "cant_get": {"ru": "Ежедневный бонус пока не доступен.", "en": "Daily bonus is not yet available."},
}

GAME = {
    "instruction": {"ru": "Для тех, кто хочет испытать свою удачу и увеличить количество получаемых токенов <b>$STN</b>.\nЕсли вы угадаете случайное число, ваша ставка увеличится в два раза. В противном случае вы проиграете.\n\nВыберите вашу ставку, а затем угадайте, будет ли выпавшее случайное число больше 52 или меньше 48.\nЕсли ваш выбор совпадает с результатом, вы побеждаете и получаете выигрыш в размере вашей ставки.", "en": "For those who want to test their luck and increase the amount of received tokens <b>$STN</b>.\nIf you guess the random number, your bet will double. Otherwise, you lose.\n\nChoose your bet, and then guess whether the random number will be greater than 52 or less than 48.\nIf your choice matches the result, you win and receive a payout equal to your bet."},
    "bet": {"ru": "Выберите ставку:", "en": "Choose your bet:"},
    "less_tokens": {"ru": "У вас недостаточно средств!", "en": "You have insufficient funds!"},
    "num": {"ru": "Угадайте число", "en": "Guess the number"},
    "bot_num": {"ru": "Загаданное число: {bot_num}", "en": "Random number: {bot_num}"},
    "again": {"ru": "Играть ещё раз", "en": "Play again"},
}

AMBASSADOR = {
    "cant": {"ru": "Чтобы получить доступ и дополнительно получать 10% от дохода ваших друзей, пригласите 100 или более пользователей!", "en": "To gain access and receive an additional 10% of your friends' income, invite 100 or more users!"},
    "already": {"ru": "Вы уже получаете 10% от дохода ваших друзей.\nПрисоединяйтесь к чату амбассадоров. Там самая актуальная информация о проекте!\n{AMBASSADOR_CHAT}", "en": "You already receive 10% of your friends' income.\nJoin the ambassadors' chat. There is the most up-to-date information about the project!\n{AMBASSADOR_CHAT}"},
    "be_amb_btn": {"ru": "Стать амбассадором", "en": "Become an ambassador"},
    "be_amb_msg": {"ru": "Вы пригласили 100 пользователей", "en": "You have invited 100 users"},
    "stay_amb": {"ru": "Теперь вы получаете 10% от дохода ваших друзей.\nПрисоединяйтесь к чату амбассадоров. Там самая актуальная информация о проекте!\n{AMBASSADOR_CHAT}", "en": "Now you receive 10% of your friends' income.\nJoin the ambassadors' chat. There is the most up-to-date information about the project!\n{AMBASSADOR_CHAT}"},
}
