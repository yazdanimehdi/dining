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
            message = "سلام دوستان و همراهان عزیز\n" \
                      "با تموم شدن این ترم ما هم به یه استراحت میریم و میخوایم ترم جدید رو با یک انرژی بیشتر و با کلی قابلیت‌های جدید بیایم پیشتون\n" \
                      "بالطبع تمامی خدمتامون تا ترم بعد متوقف می‌شه پس حواست باشه غذاهاتو خودت رزرو کنی" \
                      "از حمایت ها و همراهیاتون ممنونیم\n" \
                      "ارادتمند شما مسترزرو"
            send(message, str(user.chat_id), bot_token)

        except:
            pass
