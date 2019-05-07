import telegram
from django.db.models import Q

from dining.models import CustomUser

for user in CustomUser.objects.filter(~Q(chat_id='-')):
    if user.chat_id != 0:
        def send(msg, chat_id, token):
            bot = telegram.Bot(token=token)
            bot.send_message(chat_id=chat_id, text=msg)


        try:
            bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
            message = "سلام سلام\n" \
                      "فرا رسیدن ماه مبارک رمضان را تبریک میگویم\n" \
                      "از اونجایی که یه عده ای به هر دلیلی نمیتونن روزه بگیرن، برای سفارش ناهار گرم میتونن از بات سفارش غذا استفاده کنن 😊\n" \
                      "@orderfoodus_bot"
            send(message, str(user.chat_id), bot_token)

        except:
            pass
