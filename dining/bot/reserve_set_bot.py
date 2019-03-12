import os

import django
import telegram


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
