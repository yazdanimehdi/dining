import os
import re

import jdatetime
import telegram
from celery import task
from django.db.models import Q


@task()
def credit_insufficient():
    def send(msg, chat_id, token, keyboard):
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text=msg, reply_markup=keyboard)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    from dining.models import CustomUser, ReservedTable
    bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
    users = CustomUser.objects.filter(~Q(chat_id=0), is_paid=True)
    date = str(jdatetime.date.today() - jdatetime.timedelta(jdatetime.date.today().weekday()))
    date = re.sub(r'\-', '/', date)
    last_saturdays_date = list()
    last_saturdays_date.append(date)
    last_saturdays_date = str(last_saturdays_date)

    for user in users:
        try:
            reply_markup = telegram.ReplyKeyboardMarkup(
                [[telegram.KeyboardButton('افزایش اعتبار')]], one_time_keyboard=True)
            reserved_object = list(
                ReservedTable.objects.filter(~Q(credit=-30), week_start_date=last_saturdays_date, user=user))
            if reserved_object:
                if -15 < reserved_object[0].credit < 0:
                    message = 'اعتبار سلفت از صفر کمتره وقتشه حسابتو شارژ کنی\n' \
                              'با کلیک روی گزینه‌ی \"افزایش اعتبار\" همین الان این کارو انجام بده'
                    send(message, user.chat_id, bot_token, reply_markup)

                elif -19 < reserved_object[0].credit < -15:
                    message = 'اعتبار سلفت از -۱۵ گذشته دیگه قطعا وقتشه حسابتو شارژ کنی\n' \
                              'با کلیک روی گزینه‌ی \"افزایش اعتبار\" همین الان این کارو انجام بده'
                    send(message, user.chat_id, bot_token, reply_markup)

                elif reserved_object[0].credit < -19:
                    message = 'اعتبار سلفت از -۱۹ گذشته تا وقتی حسابتو شارژ نکنی من دیگه نمی‌تونم برات غذا رزرو کنم\n' \
                              'با کلیک روی گزینه‌ی \"افزایش اعتبار\" همین الان این کارو انجام بده'
                    send(message, user.chat_id, bot_token, reply_markup)
        except:
            pass
