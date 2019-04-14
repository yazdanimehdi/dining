import logging
import os

import django
from telegram.ext import Updater, CommandHandler

bot_token = '868024339:AAHJjjgPV2dNIqVjDIUpfENUADrYso4XQ-s'
updater = Updater(token=bot_token)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(bot, update):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    from order.models import Restaurant
    restaurant = Restaurant.objects.get(name='Radbanoo')
    restaurant.chat_id = update.message.chat_id
    restaurant.save()
    bot.sendMessage(chat_id=restaurant.chat_id,
                    text='از این به بعد سفارش‌ها برای شما از طریق همین ربات ارسال می‌گردد')


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
updater.start_polling()
updater.idle()
