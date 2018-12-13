import os

import telegram
from celery import task
from django.db.models import Q


@task()
def credit_insufficient():
    def send(msg, chat_id, token):
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text=msg)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    from dining.models import CustomUser, reserved
    bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
    users = CustomUser.objects.filter(~Q(chat_id=0), is_paid=True)

    for user in users:
        reserved_object = list(reserved.objects.filter(~Q(credit=-30), user=user, credit__level__lte=0))
        if reserved_object:
            message = 'اعتبار سلفت به ۰ رسیده وقتشه حسابتو شازژ کنی'
            send(message, user.chat_id, bot_token)

        reserved_object = list(reserved.objects.filter(~Q(credit=-30), user=user, credit__level__lte=-15))
        if reserved_object:
            message = 'اعتبار سلفت به -۱۵ رسیده دیگه قطعا وقتشه حسابتو شارژ کنی'
            send(message, user.chat_id, bot_token)

        reserved_object = list(reserved.objects.filter(~Q(credit=-30), user=user, credit__level__lte=-19))
        if reserved_object:
            message = 'اعتبار سلفت به -۱۹ رسیده تا وقتی حسابتو شارژ نکنی من دیگه نمی‌تونم برات غذا رزرو کنم'
            send(message, user.chat_id, bot_token)
