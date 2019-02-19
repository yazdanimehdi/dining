import os
import re

import jdatetime
import telegram
from celery import task
from django.db.models import Q


@task()
def credit_announcement():
    def send(msg, chat_id, token):
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text=msg)

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
            reserved_object = list(
                ReservedTable.objects.filter(~Q(credit=-30), week_start_date=last_saturdays_date, user=user))
            if reserved_object:
                message = 'اعتبار سلفت : %s' % reserved_object[0].credit
                send(message, user.chat_id, bot_token)
        except:
            pass

        user.reserve = True
        user.save()

        def send_stop(chat_id, token):
            bot = telegram.Bot(token=token)
            reply_markup = telegram.ReplyKeyboardMarkup(
                [[telegram.KeyboardButton('/stop_reserve')]], one_time_keyboard=True)

            bot.sendMessage(chat_id=chat_id,
                            text="برای رزرو نکردن هفته‌ی آینده \"توقف رزرو\" رو ارسال کن",
                            reply_markup=reply_markup,
                            parse_mode=telegram.ParseMode.MARKDOWN)

        try:
            send_stop(user.chat_id, bot_token)
        except Exception as e:
            print(e)
