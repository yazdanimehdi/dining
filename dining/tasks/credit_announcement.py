import os

import telegram
from celery import task
from django.db.models import Q


@task()
def credit_announcement():
    def send(msg, chat_id, token):
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text=msg)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    from dining.models import CustomUser, reserved
    bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
    users = CustomUser.objects.filter(~Q(chat_id=0), is_paid=True)

    for user in users:
        reserved_object = list(reserved.objects.filter(~Q(credit=-30), user=user))
        if reserved_object:
            message = 'اعتبار سلفت : %s' % reserved_object[0].credit
            send(message, user.chat_id, bot_token)
