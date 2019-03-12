import os
from enum import IntEnum

import django
import telegram
from telegram.ext import ConversationHandler


class BotStateCharge(IntEnum):
    CHARGE = 1


def request_payment(bot, update, user_data):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.models import CustomUser
    user_data['user'] = CustomUser.objects.get(chat_id=update.message.chat_id)
    keyboard = [[telegram.InlineKeyboardButton(text='۵۰۰۰ تومن', callback_data=5000)],
                [telegram.InlineKeyboardButton(text='۱۰۰۰۰ تومن', callback_data=10000)],
                [telegram.InlineKeyboardButton(text='۱۵۰۰۰ تومن', callback_data=15000)],
                [telegram.InlineKeyboardButton(text='۲۰۰۰۰ تومن', callback_data=20000)],
                ]
    inline_keyboard = telegram.InlineKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="*لطفا مبلغ مورد نظر را انتخاب کنید:*",
                    reply_markup=inline_keyboard,
                    parse_mode=telegram.ParseMode.MARKDOWN)
    return BotStateCharge.CHARGE


def payment_result(bot, update, user_data):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.models import UserDiningData
    from dining.views import charge_account
    u = UserDiningData.objects.get(user=user_data['user'])
    query = update.callback_query
    amount = query['data']
    user = u.dining_username
    password = u.dining_password
    link = charge_account(user, password, amount)
    bot.sendMessage(chat_id=user_data['user'].chat_id,
                    text="برای پرداخت روی لینک زیر کلیک کنید:\n"
                         "*توجه داشته باشید بعد از پرداخت روی گزینه‌ي تکمیل فرایند خرید کلیک کرده و"
                         "حتما وارد سامانه‌ی غذا شوید تا اعتبار به حسابتان واریز گردد*",
                    parse_mode=telegram.ParseMode.MARKDOWN)
    bot.sendMessage(chat_id=user_data['user'].chat_id,
                    text=link)
    return ConversationHandler.END
