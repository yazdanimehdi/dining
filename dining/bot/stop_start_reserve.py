import os

import django
import telegram


def stop_reserve(bot, update):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.models import CustomUser
    u = CustomUser.objects.filter(chat_id=update.message.chat_id)
    u[0].reserve = False
    u[0].save()
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="خب هفته‌ي بعد رو برات رزرو نمی‌کنم "
                         "اگه می‌خوای هفته‌ي بعد رو برات رزرو کنم \"شروع رزرو\" رو ارسال کن",
                    parse_mode=telegram.ParseMode.MARKDOWN)


def start_reserve(bot, update):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from dining.models import CustomUser
    u = CustomUser.objects.filter(chat_id=update.message.chat_id)
    u[0].reserve = True
    u[0].save()
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="خب ازاین به بعد دوباره برات غذا رزرو میکنم",
                    parse_mode=telegram.ParseMode.MARKDOWN)
