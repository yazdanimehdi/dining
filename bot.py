import logging
import os

import django
import telegram
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler

bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
updater = Updater(token=bot_token)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(bot, update):
    reply_markup = telegram.ReplyKeyboardMarkup(
        [[telegram.KeyboardButton('شمارتو به اشتراک بذار', request_contact=True)]], one_time_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="*سلام٬مسترزرو هستم \n"
                         "برای این که بتونم به حساب کاربریت متصل شم باید اجازه بدی به شمارت دسترسی داشته باشم*",
                    reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)


def get_phone(bot, update):
    if update.message.contact.phone_number[0] == '+':
        phone = '0' + update.message.contact.phone_number[3:]
    else:
        phone = '0' + update.message.contact.phone_number[2:]
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.models import CustomUser
    u = list(CustomUser.objects.filter(phone=phone))
    if u:
        chat_id = update.message.chat_id
        u[0].chat_id = int(chat_id)
        u[0].save()
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="*خب به حساب کاربریت وصل شدم\n"
                             "از این به بعد هر روزی که غذا رزرو کنم واست بهت اطلاعاتش رو میدم\n"
                             "و هر هفته اطلاعات حساب سلف رو واست میفرستم که در صورت نیاز اعتبارت رو شارژ کنی\n"
                             "اگر حواست نبود من در ۳ مرحله بهت هشدار میدم\n"
                             "اولین مرحله وقتی حسابت به صفر برسه\n"
                             "دومین هشدار وقتی که به منفی ۱۵ برسی\n"
                             "و هشدار آخر وقتی که منفی ۲۰ شدی\n"
                             "من از اون لحظه به بعد قادر به رزرو غذا نیستم. تا وقتی دوباره اعتبارت رو افزایش بدی\n"
                             "فقط یادت باشه که منو متوقف نکنی چون اونطوری دیگه نمی‌تونم بهت خدمت بدم\n"
                             "دوستدار شما\n"
                             "*mrzoro",
                        parse_mode=telegram.ParseMode.MARKDOWN)

    else:
        reply_markup = telegram.ReplyKeyboardMarkup(
            [[telegram.KeyboardButton('شمارتو به اشتراک بذار', request_contact=True)]], one_time_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="*شماره‌ی حساب کاربریت با شماره‌ی تلگرامت فرق می‌کنه"
                             "\nبرای استفاده از امکان تلگرامی ما شماره‌ی حساب کاربریتو به شماره‌ی تلگرامت تغییر بده "
                             "و دوباره تلاش کن*",
                        reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)


def stop_reserve(bot, update):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.models import CustomUser
    u = CustomUser.objects.filter(chat_id=update.message.chat_id)
    u[0].reserve = False
    u[0].save()
    reply_markup = telegram.ReplyKeyboardMarkup(
        [[telegram.KeyboardButton('/start_reserve')]], one_time_keyboard=False)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="خب هفته‌ي بعد رو برات رزرو نمی‌کنم اگه می‌خوای هفته‌ي بعد رو برات رزرو کنم گزینه‌ی شروع رزرو رو انتخاب کن",
                    reply_markup=reply_markup,
                    parse_mode=telegram.ParseMode.MARKDOWN)


def start_reserve(bot, update):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.models import CustomUser
    u = CustomUser.objects.filter(chat_id=update.message.chat_id)
    u[0].reserve = True
    u[0].save()
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="خب ازاین به بعد دوباره برات غذا رزرو میکنم",
                    parse_mode=telegram.ParseMode.MARKDOWN)


start_handler = CommandHandler('start', start)
contact_handler = MessageHandler(Filters.contact, get_phone)
stop_handler = CommandHandler('stop_reserve', stop_reserve)
start_reserve_handler = CommandHandler('start_reserve', start_reserve)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(contact_handler)
dispatcher.add_handler(stop_handler)
dispatcher.add_handler(start_reserve_handler)
updater.start_polling()
