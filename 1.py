import telegram
from django.db.models import Q

from dining.models import CustomUser

for user in CustomUser.objects.filter(~Q(chat_id=0)):
    if user.chat_id != 0:
        def send(msg, chat_id, token):
            bot = telegram.Bot(token=token)
            bot.send_message(chat_id=chat_id, text=msg)


        try:
            bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
            message = "سلام سلام\n" \
                      "به مناسبت تولد امام حسن\n" \
                      "ربات سفارش غذا از فردا با ۲۰ درصد تخفیف در خدمت شماست\n" \
                      "@orderfoodus_bot"
            send(message, str(user.chat_id), bot_token)

        except:
            pass
