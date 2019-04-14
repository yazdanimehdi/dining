import os

import django
import telegram

bot_token = '868024339:AAHJjjgPV2dNIqVjDIUpfENUADrYso4XQ-s'


def send_function():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
    django.setup()
    bot = telegram.Bot(token=bot_token)
    from order.models import Invoice, OrderFood, Restaurant
    chat_id = Restaurant.objects.get(name='Radbanoo').chat_id
    invoices = Invoice.objects.filter(is_active=True, is_sent=False)
    for invoice in invoices:
        is_paid = invoice.is_paid
        adress = invoice.address
        order = OrderFood.objects.filter(invoice=invoice)
        text = 'سفارش‌ها به این ترتیب می‌باشند:'
        for item in order:
            text += item.food.name + '\n' + '----------------------' + '\n'

        text += f'{invoice.user.name} :نام و نام خانوادگی:' + '\n' + f'{invoice.user.phone} :شماره تماس' + '\n'
        text += f'{invoice.address} :آدرس' + '\n'
        if invoice.is_paid is True:
            text += 'مبلغ پرداخت شده است وجه نقد دریافت نفرمایید'
        invoice.is_sent = True
        invoice.save()

        bot.sendMessage(chat_id=chat_id,
                        text=text)
