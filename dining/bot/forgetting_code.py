import os
from enum import IntEnum

import django
import telegram
from telegram.ext import ConversationHandler


class BotStateForget(IntEnum):
    MEAL = 3
    FORGETCODE = 4


def start_forget(bot, update, user_data):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.models import CustomUser, UserDiningData, UserSelfs
    user_data['user'] = CustomUser.objects.filter(chat_id=update.message.chat_id)[0]
    user_data['username'] = UserDiningData.objects.get(user=user_data['user']).dining_username
    user_data['password'] = UserDiningData.objects.get(user=user_data['user']).dining_password
    selfs = UserSelfs.objects.filter(user=user_data['user'], is_active=True)
    keyboard = list()
    for item in selfs:
        keyboard.append([telegram.InlineKeyboardButton(text=f'{item.self_name}',
                                                       callback_data=f'{item.self_id}')])
    inline_keyboard = telegram.InlineKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="*لطفا سلفی که می‌خوای کد فراموشی بگیری رو انتخاب کن:*",
                    reply_markup=inline_keyboard,
                    parse_mode=telegram.ParseMode.MARKDOWN)
    return BotStateForget.MEAL


def meal_select(bot, update, user_data):
    query = update.callback_query
    user_data['self'] = query['data']
    keyboard = [[telegram.InlineKeyboardButton(text='ناهار', callback_data=1)],
                [telegram.InlineKeyboardButton(text='شام', callback_data=2)]]
    inline_keyboard = telegram.InlineKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.sendMessage(chat_id=user_data['user'].chat_id,
                    text="*لطفا وعده‌ی غذایی که می‌خوای کد فراموشی بگیری رو انتخاب کن:*",
                    reply_markup=inline_keyboard,
                    parse_mode=telegram.ParseMode.MARKDOWN)
    return BotStateForget.FORGETCODE


def forget_code(bot, update, user_data):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.views import forget
    query = update.callback_query
    user_data['meal'] = query['data']
    bot.sendMessage(chat_id=user_data['user'].chat_id,
                    text="*در حال آوردن کد فرآموشی لطفا منتظر باش*",
                    parse_mode=telegram.ParseMode.MARKDOWN)
    forget_code_text = \
        forget(user=user_data['username'], password=user_data['password'], self=user_data['self'],
               meal=user_data['meal'])
    bot.sendMessage(chat_id=user_data['user'].chat_id,
                    text=f"*:کد فراموشیت*",
                    parse_mode=telegram.ParseMode.MARKDOWN)
    bot.sendMessage(chat_id=user_data['user'].chat_id,
                    text=f"*{forget_code_text}*",
                    parse_mode=telegram.ParseMode.MARKDOWN)
    return ConversationHandler.END
