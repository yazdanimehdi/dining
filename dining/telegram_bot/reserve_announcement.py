import os

import jdatetime
import telegram
from celery import task
from django.db.models import Q


@task()
def reserve_announcement():
    def send(msg, chat_id, token):
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text=msg)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    from dining.models import CustomUser, reserved

    bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
    users = CustomUser.objects.filter(~Q(chat_id=0), is_paid=True)

    for user in users:
        last_saturdays_date = str(jdatetime.date.today() - jdatetime.timedelta(jdatetime.date.today().weekday()))
        reserved_data = reserved.objects.get(week_start_date=last_saturdays_date, user=user)

        if int(jdatetime.date.today().weekday()) == 0:
            breakfast = reserved_data.sunday_breakfast
            lunch = reserved_data.saturday_lunch
            dinner = reserved_data.saturday_dinner
            if (dinner or breakfast or lunch) != "-":
                message = "غذاهای رزرو شده امروز:\n" \
                          "صبحانه‌ی فردا: %s \n" \
                          "ناهار امروز: %s \n" \
                          "شام امروز: %s \n" % (breakfast, lunch, dinner)
                send(message, str(user.chat_id), bot_token)

        elif int(jdatetime.date.today().weekday()) == 1:
            breakfast = reserved_data.monday_breakfast
            lunch = reserved_data.sunday_lunch
            dinner = reserved_data.sunday_dinner
            if (dinner or breakfast or lunch) != "-":
                message = "غذاهای رزرو شده امروز:\n" \
                          "صبحانه‌ی فردا: %s \n" \
                          "ناهار امروز: %s \n" \
                          "شام امروز: %s \n" % (breakfast, lunch, dinner)
                send(message, str(user.chat_id), bot_token)

        elif int(jdatetime.date.today().weekday()) == 2:
            breakfast = reserved_data.tuesday_breakfast
            lunch = reserved_data.monday_lunch
            dinner = reserved_data.monday_dinner
            if (dinner or breakfast or lunch) != "-":
                message = "غذاهای رزرو شده امروز:\n" \
                          "صبحانه‌ی فردا: %s \n" \
                          "ناهار امروز: %s \n" \
                          "شام امروز: %s \n" % (breakfast, lunch, dinner)
                send(message, str(user.chat_id), bot_token)

        elif int(jdatetime.date.today().weekday()) == 3:
            breakfast = reserved_data.wednesday_breakfast
            lunch = reserved_data.tuesday_lunch
            dinner = reserved_data.tuesday_dinner
            if (dinner or breakfast or lunch) != "-":
                message = "غذاهای رزرو شده امروز:\n" \
                          "صبحانه‌ی فردا: %s \n" \
                          "ناهار امروز: %s \n" \
                          "شام امروز: %s \n" % (breakfast, lunch, dinner)
                send(message, str(user.chat_id), bot_token)

        elif int(jdatetime.date.today().weekday()) == 4:
            breakfast = reserved_data.thursday_breakfast
            lunch = reserved_data.wednesday_lunch
            dinner = reserved_data.wednesday_dinner
            if (dinner or breakfast or lunch) != "-":
                message = "غذاهای رزرو شده امروز:\n" \
                          "صبحانه‌ی فردا: %s \n" \
                          "ناهار امروز: %s \n" \
                          "شام امروز: %s \n" % (breakfast, lunch, dinner)
                send(message, str(user.chat_id), bot_token)

        elif int(jdatetime.date.today().weekday()) == 5:
            breakfast = reserved_data.friday_breakfast
            lunch = reserved_data.thursday_lunch
            dinner = reserved_data.thursday_dinner
            if (dinner or breakfast or lunch) != "-":
                message = "غذاهای رزرو شده امروز:\n" \
                          "صبحانه‌ی فردا: %s \n" \
                          "ناهار امروز: %s \n" \
                          "شام امروز: %s \n" % (breakfast, lunch, dinner)
                send(message, str(user.chat_id), bot_token)

        elif int(jdatetime.date.today().weekday()) == 6:
            breakfast = reserved_data.saturday_breakfast
            lunch = reserved_data.friday_lunch
            dinner = reserved_data.friday_dinner
            if (dinner or breakfast or lunch) != "-":
                message = "غذاهای رزرو شده امروز:\n" \
                          "صبحانه‌ی فردا: %s \n" \
                          "ناهار امروز: %s \n" \
                          "شام امروز: %s \n" % (breakfast, lunch, dinner)
                send(message, str(user.chat_id), bot_token)
