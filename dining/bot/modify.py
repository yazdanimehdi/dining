import os
from enum import IntEnum

import django
import telegram
from telegram.ext import ConversationHandler


class BotStateModify(IntEnum):
    SELECTMEAL = 1
    SELECTDAY = 2
    SELECT = 3
    SELECTFOOD = 4
    MODIFY = 5
    CANCEL = 6
    RESERVE = 7
    MODIFYEND = 8


def select_self(bot, update, user_data):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.models import CustomUser, UserSelfs
    user_data['user'] = CustomUser.objects.filter(chat_id=update.message.chat_id)[0]
    selfs = UserSelfs.objects.filter(user=user_data['user'], is_active=True)
    keyboard = list()
    for item in selfs:
        keyboard.append([telegram.InlineKeyboardButton(text=f'{item.self_name}',
                                                       callback_data=f'{item.self_id}')])
    inline_keyboard = telegram.InlineKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="*لطفا سلفی که می‌خوای غذا داخلش تغییر بدی رو انتخاب کن*",
                    reply_markup=inline_keyboard,
                    parse_mode=telegram.ParseMode.MARKDOWN)
    return BotStateModify.SELECTMEAL


def select_meal(bot, update, user_data):
    query = update.callback_query
    user_data['self'] = query['data']
    keyboard = [[telegram.InlineKeyboardButton(text='ناهار', callback_data='data_lunch')],
                [telegram.InlineKeyboardButton(text='شام', callback_data='data_dinner')]]
    inline_keyboard = telegram.InlineKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.sendMessage(chat_id=user_data['user'].chat_id,
                    text="*لطفا وعده‌ی غذایی که می‌خوای ویرایش کنی رو انتخاب کن:*",
                    reply_markup=inline_keyboard,
                    parse_mode=telegram.ParseMode.MARKDOWN)
    return BotStateModify.SELECTDAY


def select_day(bot, update, user_data):
    query = update.callback_query
    user_data['meal'] = query['data']
    keyboard = [[telegram.InlineKeyboardButton(text='شنبه', callback_data='شنبه')],
                [telegram.InlineKeyboardButton(text='یک شنبه', callback_data='یک شنبه')],
                [telegram.InlineKeyboardButton(text='دوشنبه', callback_data='دوشنبه')],
                [telegram.InlineKeyboardButton(text='سه شنبه', callback_data='سه شنبه')],
                [telegram.InlineKeyboardButton(text='چهارشنبه', callback_data='چهارشنبه')],
                [telegram.InlineKeyboardButton(text='پنج شنبه', callback_data='پنج شنبه')],
                [telegram.InlineKeyboardButton(text='جمعه', callback_data='جمعه')]
                ]
    inline_keyboard = telegram.InlineKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.sendMessage(chat_id=user_data['user'].chat_id,
                    text="*لطفا روزی که می‌خوای ویرایش کنی رو انتخاب کن:*",
                    reply_markup=inline_keyboard,
                    parse_mode=telegram.ParseMode.MARKDOWN)
    return BotStateModify.SELECT


def select_modify(bot, update, user_data):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.models import Key
    query = update.callback_query
    user_data['day'] = query['data']
    user_data['data'] = Key.objects.get(container__name=user_data['user'].username + user_data['meal'],
                                        key=user_data['day'])
    keyboard = [[telegram.InlineKeyboardButton(text='تغییر', callback_data='1')],
                [telegram.InlineKeyboardButton(text='رزرو', callback_data='2')],
                [telegram.InlineKeyboardButton(text='لفو رزرو', callback_data='3')]]
    inline_keyboard = telegram.InlineKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.sendMessage(chat_id=user_data['user'].chat_id,
                    text="*لطفا عملیات مورد نظر رو انتخاب کن:*",
                    reply_markup=inline_keyboard,
                    parse_mode=telegram.ParseMode.MARKDOWN)
    return BotStateModify.SELECTFOOD


def modify(bot, update, user_data):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.models import Val
    data = Val.objects.filter(container__name=user_data['user'].username + user_data['meal'],
                              key=user_data['data'])
    query = update.callback_query
    if query['data'] == '1':

        keyboard = list()
        for item in data:
            keyboard.append([telegram.InlineKeyboardButton(text=f'{item.name}',
                                                           callback_data=f'{item.food_id}')])

        bot.sendMessage(chat_id=user_data['user'].chat_id,
                        text="*لطفا غذای رزرو شده‌ي کنونی رو انتخاب کن:*",
                        reply_markup=keyboard,
                        parse_mode=telegram.ParseMode.MARKDOWN)

        return BotStateModify.MODIFY

    if query['data'] == '3':

        keyboard = list()
        for item in data:
            keyboard.append([telegram.InlineKeyboardButton(text=f'{item.name}',
                                                           callback_data=f'{item.food_id}')])

        bot.sendMessage(chat_id=user_data['user'].chat_id,
                        text="*لطفا غذایی رو که  میخوای رزروشو کنسل کنی رو انتخاب کن:*",
                        reply_markup=keyboard,
                        parse_mode=telegram.ParseMode.MARKDOWN)

        return BotStateModify.CANCEL

    if query['data'] == '2':
        keyboard = list()
        for item in data:
            keyboard.append([telegram.InlineKeyboardButton(text=f'{item.name}',
                                                           callback_data=f'{item.food_id}')])

        bot.sendMessage(chat_id=user_data['user'].chat_id,
                        text="*لطفا غذایی رو که  میخوای رزرو کنی رو انتخاب کن:*",
                        reply_markup=keyboard,
                        parse_mode=telegram.ParseMode.MARKDOWN)

        return BotStateModify.RESERVE


def reserve(bot, update, user_data):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.views import do_reserve
    query = update.callback_query
    do_reserve(user_data['user'], query['data'], user_data['self'])
    bot.sendMessage(chat_id=user_data['user'].chat_id,
                    text="*رزرو با موفقیت انجام شد(در صورتی که اعتبار نداشته باشی این رزرو صورت نگرفته*",
                    parse_mode=telegram.ParseMode.MARKDOWN)
    return ConversationHandler.END


def cancel_reserve(bot, update, user_data):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.views import cancel_reserve
    query = update.callback_query
    cancel_reserve(query['data'], user_data['user'])
    bot.sendMessage(chat_id=user_data['user'].chat_id,
                    text="*رزرو با موفقیت لغو شد*",
                    parse_mode=telegram.ParseMode.MARKDOWN)
    return ConversationHandler.END


def modify_reserve(bot, update, user_data):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.models import Val
    query = update.callback_query
    user_data['cancel_id'] = query['data']
    data = Val.objects.filter(container__name=user_data['user'].username + user_data['meal'],
                              key=user_data['data'])
    keyboard = list()
    for item in data:
        keyboard.append([telegram.InlineKeyboardButton(text=f'{item.name}',
                                                       callback_data=f'{item.food_id}')])

    bot.sendMessage(chat_id=user_data['user'].chat_id,
                    text="*لطفا غذایی که میخوای رزرو شه رو انتخاب کن:*",
                    reply_markup=keyboard,
                    parse_mode=telegram.ParseMode.MARKDOWN)

    return BotStateModify.MODIFYEND


def modify_reserve_end(bot, update, user_data):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.views import modify_reserve
    query = update.callback_query
    modify_reserve(user_data['user'], user_data['cancel_id'], query['data'], user_data['self'])
    bot.sendMessage(chat_id=user_data['user'].chat_id,
                    text="*رزرو با موفقیت لغو شد*",
                    parse_mode=telegram.ParseMode.MARKDOWN)
    return ConversationHandler.END
