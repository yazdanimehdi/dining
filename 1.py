import telegram

from dining.models import CustomUser

for user in CustomUser.objects.filter(is_paid=True):
    if user.chat_id != 0:
        def send(msg, chat_id, token):
            bot = telegram.Bot(token=token)
            bot.send_message(chat_id=chat_id, text=msg)


        bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
        message = "*سلام\n" \
                  "با عرض پوزش دیروز به دلایل فنی ربات در دسترس نبود \n" \
                  "برای رزرو نکردن هفته‌ی آینده \"توقف رزرو\" رو ارسال کن*"
        send(message, str(user.chat_id), bot_token)
