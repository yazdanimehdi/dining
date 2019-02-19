import os
import re

import jdatetime
import telegram
from celery import task
from django.db.models import Q


@task()
def reserve_announcement():
    def send(msg, chat_id, token, keyboard):
        bot = telegram.Bot(token=token)
        bot.sendMessage(chat_id=chat_id, text=msg, reply_markup=keyboard)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    from dining.models import CustomUser, ReservedTable

    bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
    users = CustomUser.objects.filter(~Q(chat_id=0), is_paid=True)

    for user in users:
        date = str(jdatetime.date.today() - jdatetime.timedelta(jdatetime.date.today().weekday()))
        date = re.sub(r'\-', '/', date)
        last_saturdays_date = list()
        last_saturdays_date.append(date)
        last_saturdays_date = str(last_saturdays_date)
        reserved_data = ReservedTable.objects.filter(week_start_date=last_saturdays_date, user=user)
        try:
            if reserved_data:
                reply_markup = telegram.ReplyKeyboardMarkup(
                    [[telegram.KeyboardButton('کد فراموشی')]], one_time_keyboard=True)
                if int(jdatetime.date.today().weekday()) == 0:
                    breakfast = reserved_data[0].sunday_breakfast
                    lunch = reserved_data[0].saturday_lunch
                    dinner = reserved_data[0].saturday_dinner
                    if dinner != "-" or breakfast != "-" or lunch != "-":
                        message = "غذاهای رزرو شده امروز:\n" \
                                  "صبحانه‌ی فردا: %s \n" \
                                  "ناهار امروز: %s \n" \
                                  "شام امروز: %s \n" % (breakfast, lunch, dinner)
                        send(message, str(user.chat_id), bot_token, reply_markup)

                elif int(jdatetime.date.today().weekday()) == 1:
                    breakfast = reserved_data[0].monday_breakfast
                    lunch = reserved_data[0].sunday_lunch
                    dinner = reserved_data[0].sunday_dinner
                    if dinner != "-" or breakfast != "-" or lunch != "-":
                        message = "غذاهای رزرو شده امروز:\n" \
                                  "صبحانه‌ی فردا: %s \n" \
                                  "ناهار امروز: %s \n" \
                                  "شام امروز: %s \n" % (breakfast, lunch, dinner)
                        send(message, str(user.chat_id), bot_token, reply_markup)

                elif int(jdatetime.date.today().weekday()) == 2:
                    breakfast = reserved_data[0].tuesday_breakfast
                    lunch = reserved_data[0].monday_lunch
                    dinner = reserved_data[0].monday_dinner
                    if dinner != "-" or breakfast != "-" or lunch != "-":
                        message = "غذاهای رزرو شده امروز:\n" \
                                  "صبحانه‌ی فردا: %s \n" \
                                  "ناهار امروز: %s \n" \
                                  "شام امروز: %s \n" % (breakfast, lunch, dinner)
                        send(message, str(user.chat_id), bot_token)

                elif int(jdatetime.date.today().weekday()) == 3:
                    breakfast = reserved_data[0].wednesday_breakfast
                    lunch = reserved_data[0].tuesday_lunch
                    dinner = reserved_data[0].tuesday_dinner
                    if dinner != "-" or breakfast != "-" or lunch != "-":
                        message = "غذاهای رزرو شده امروز:\n" \
                                  "صبحانه‌ی فردا: %s \n" \
                                  "ناهار امروز: %s \n" \
                                  "شام امروز: %s \n" % (breakfast, lunch, dinner)
                        send(message, str(user.chat_id), bot_token, reply_markup)

                elif int(jdatetime.date.today().weekday()) == 4:
                    breakfast = reserved_data[0].thursday_breakfast
                    lunch = reserved_data[0].wednesday_lunch
                    dinner = reserved_data[0].wednesday_dinner
                    if dinner != "-" or breakfast != "-" or lunch != "-":
                        message = "غذاهای رزرو شده امروز:\n" \
                                  "صبحانه‌ی فردا: %s \n" \
                                  "ناهار امروز: %s \n" \
                                  "شام امروز: %s \n" % (breakfast, lunch, dinner)
                        send(message, str(user.chat_id), bot_token, reply_markup)

                elif int(jdatetime.date.today().weekday()) == 5:
                    breakfast = reserved_data[0].friday_breakfast
                    lunch = reserved_data[0].thursday_lunch
                    dinner = reserved_data[0].thursday_dinner
                    if dinner != "-" or breakfast != "-" or lunch != "-":
                        message = "غذاهای رزرو شده امروز:\n" \
                                  "صبحانه‌ی فردا: %s \n" \
                                  "ناهار امروز: %s \n" \
                                  "شام امروز: %s \n" % (breakfast, lunch, dinner)
                        send(message, str(user.chat_id), bot_token, reply_markup)

                elif int(jdatetime.date.today().weekday()) == 6:
                    breakfast = reserved_data[0].saturday_breakfast
                    lunch = reserved_data[0].friday_lunch
                    dinner = reserved_data[0].friday_dinner
                    if dinner != "-" or breakfast != "-" or lunch != "-":
                        message = "غذاهای رزرو شده امروز:\n" \
                                  "صبحانه‌ی فردا: %s \n" \
                                  "ناهار امروز: %s \n" \
                                  "شام امروز: %s \n" % (breakfast, lunch, dinner)
                        send(message, str(user.chat_id), bot_token, reply_markup)
        except:
            pass
