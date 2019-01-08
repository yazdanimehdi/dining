import re

import jdatetime
import telegram
from django.db.models import Q

from dining.models import CustomUser, ReservedTable


def send(msg, chat_id, token):
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)


bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
users = CustomUser.objects.filter(~Q(chat_id=0), is_paid=True)
date = str(jdatetime.date.today() - jdatetime.timedelta(jdatetime.date.today().weekday()))
date = re.sub(r'\-', '/', date)
last_saturdays_date = list()
last_saturdays_date.append(date)
last_saturdays_date = str(last_saturdays_date)

for user in users:
    reserved_object = list(ReservedTable.objects.filter(~Q(credit=-30), week_start_date=last_saturdays_date, user=user,
                                                        credit__level__lte=0))
    if reserved_object:
        message = 'اعتبار سلفت به ۰ رسیده وقتشه حسابتو شازژ کنی'
        send(message, user.chat_id, bot_token)

    reserved_object = list(
        ReservedTable.objects.filter(~Q(credit=-30), user=user, week_start_date=last_saturdays_date,
                                     credit__level__lte=-15))
    if reserved_object:
        message = 'اعتبار سلفت به -۱۵ رسیده دیگه قطعا وقتشه حسابتو شارژ کنی'
        send(message, user.chat_id, bot_token)

    reserved_object = list(
        ReservedTable.objects.filter(~Q(credit=-30), user=user, week_start_date=last_saturdays_date,
                                     credit__level__lte=-19))
    if reserved_object:
        message = 'اعتبار سلفت به -۱۹ رسیده تا وقتی حسابتو شارژ نکنی من دیگه نمی‌تونم برات غذا رزرو کنم'
        send(message, user.chat_id, bot_token)
