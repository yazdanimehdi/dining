import telegram

from dining.models import CustomUser

for user in CustomUser.objects.filter(is_paid=True):
    if user.chat_id != 0:
        def send(msg, chat_id, token):
            bot = telegram.Bot(token=token)
            bot.send_message(chat_id=chat_id, text=msg)


        try:
            bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
            message = "*مسترزرو سال خوبی رو برای شما و خانواده محترمتون آرزو میکنه 🖤♥️\n" \
                      "سال ۹۸ با ۱۰۰ درصد انرژی، همراه با هم به سوی پیشرفت قدم برمیداریم*"
            send(message, str(user.chat_id), bot_token)

        except:
            pass
