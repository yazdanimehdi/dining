import datetime

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        import logging
        import os
        from enum import IntEnum

        import django
        import telegram
        from telegram.ext import Updater, Filters, MessageHandler, CallbackQueryHandler, ConversationHandler, \
            CommandHandler

        bot_token = '884113858:AAG05koed7NLj6o3n8y5l7YegKa3OOfd36M'
        updater = Updater(token=bot_token)
        dispatcher = updater.dispatcher
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        class BotState(IntEnum):
            INITIALIZE = 1
            SIGNUP = 2
            SIGNUP_NAME = 3
            SIGNUP_PHONE = 4
            ORDER = 5
            MENU_TYPE = 6
            MENU = 7
            EDIT = 8
            CONFIRM = 9
            PAYMENT = 10
            PAYMENT_CONFIRM = 11
            DETAIL = 12
            ADDRESS = 13

        def start_order(bot, update, user_data):
            if 11 < datetime.datetime.now().time().hour < 16 or 17 < datetime.datetime.now().time().hour < 20:
                user_data.clear()
                reply_markup = telegram.ReplyKeyboardMarkup(
                    [[telegram.KeyboardButton(text='سفارش')],
                     [telegram.KeyboardButton(text='مشاهده‌ی سبد خرید'),
                      telegram.KeyboardButton(text='خالی کردن سبد خرید')]], resize_keyboard=True)
                bot.sendMessage(chat_id=update.message.chat_id,
                                text="*برای سفارش گزینه‌اش رو انتخاب کن*", reply_markup=reply_markup,
                                parse_mode=telegram.ParseMode.MARKDOWN)
                return BotState.INITIALIZE
            else:
                bot.sendMessage(chat_id=update.message.chat_id,
                                text="*زمان سفارش گذشته!\n"
                                     "ساعت کاری ما در ماه مبارک رمضان ظهرها از ساعت ۱۲ تا ۳ هست\n"
                                     "و غروب‌ها از ساعت ۶ تا ۸ هست*",
                                parse_mode=telegram.ParseMode.MARKDOWN)
                return ConversationHandler.END

        def menu(bot, update, user_data):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
            django.setup()
            from order.models import FoodUser, RestaurantUniversityCoverage
            try:
                user = FoodUser.objects.get(chat_id=update.message.chat_id)
                user_data['user'] = user
                coverage = RestaurantUniversityCoverage.objects.all()
                uni = list()
                for item in coverage:
                    if item.university.name not in uni:
                        uni.append(item.university.name)
                keyboard = list()
                for item in uni:
                    keyboard.append([telegram.InlineKeyboardButton(text=f'{item}',
                                                                   callback_data=f'{item}')])
                inline_keyboard = telegram.InlineKeyboardMarkup(keyboard, resize_keyboard=True)
                bot.sendMessage(chat_id=update.message.chat_id,
                                text="*لطفا دانشگاهتو انتخاب کن:*",
                                reply_markup=inline_keyboard,
                                parse_mode=telegram.ParseMode.MARKDOWN)
                return BotState.MENU_TYPE

            except FoodUser.DoesNotExist:
                reply_markup = telegram.ReplyKeyboardMarkup(
                    [[telegram.KeyboardButton('ثبت نام')]])
                bot.sendMessage(chat_id=update.message.chat_id,
                                text="*برای سفارش غذا اول باید ثبت‌نام کنی*",
                                reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
                return BotState.SIGNUP

        def select_food_type(bot, update, user_data):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
            django.setup()
            from order.models import RestaurantUniversityCoverage
            user = user_data['user']
            query = update.callback_query
            coverage = RestaurantUniversityCoverage.objects.filter(university__name=query['data'])
            restaurant = coverage[0].restaurant
            user_data['restaurant'] = restaurant
            inline_keyboard_food = telegram.InlineKeyboardMarkup(
                [[telegram.InlineKeyboardButton(text='غذای اصلی', callback_data='main')],
                 [telegram.InlineKeyboardButton(text='دسر و نوشیدنی', callback_data='desert')]])
            bot.sendMessage(chat_id=user.chat_id,
                            text=f"*لطفا دسته بندی مورد نظر را انتخاب کنید*",
                            reply_markup=inline_keyboard_food,
                            parse_mode=telegram.ParseMode.MARKDOWN)
            return BotState.MENU

        def select_food(bot, update, user_data):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
            django.setup()
            from order.models import RestaurantMenu
            user = user_data['user']
            restaurant = user_data['restaurant']
            query = update.callback_query
            try:
                food_type = user_data['choice']
            except KeyError:
                food_type = query['data']
            menu_user = RestaurantMenu.objects.filter(restaurant=restaurant, food_type=food_type, is_active=True)
            for food in menu_user:
                user_data[f'{food.name}'] = 0
                inline_keyboard = telegram.InlineKeyboardMarkup(
                    [[telegram.InlineKeyboardButton(text='-', callback_data='-1'),
                      telegram.InlineKeyboardButton(text='0', callback_data='num'),
                      telegram.InlineKeyboardButton(text='+', callback_data='+1')]]
                    , resize_keyboard=True)
                bot.sendMessage(chat_id=query['message']['chat']['id'],
                                text=f"* {food.name} ------------- {int(food.price)} تومن *",
                                reply_markup=inline_keyboard, parse_mode=telegram.ParseMode.MARKDOWN)
            inline_keyboard_confirm = telegram.InlineKeyboardMarkup(
                [[telegram.InlineKeyboardButton(text='غذای اصلی', callback_data='main'),
                  telegram.InlineKeyboardButton(text='دسر و نوشیدنی', callback_data='desert')],
                 [telegram.InlineKeyboardButton(text='تایید و اضافه کردن توضیحات', callback_data='detail')],
                 [telegram.InlineKeyboardButton(text='تایید', callback_data='ok')],
                 [telegram.InlineKeyboardButton(text='انصراف', callback_data='cancel')]], resize_keyboard=True)
            bot.sendMessage(chat_id=query['message']['chat']['id'], text='*لطفا گزینه‌ی مورد نظر رو انتخاب کن*',
                            parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=inline_keyboard_confirm)
            return BotState.EDIT

        def add_or_remove_item(bot, update, user_data):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
            django.setup()
            user = user_data['user']
            query = update.callback_query
            inline_message_id = query.message.message_id
            food = query.message.text.split('-------------')[0].strip()
            inline_chat_id = query.message.chat_id
            if food in user_data:
                quantity = user_data[f'{food}']
            if query['data'] == '+1':
                quantity += 1
                user_data[f'{food}'] = quantity
                inline_keyboard = telegram.InlineKeyboardMarkup(
                    [[telegram.InlineKeyboardButton(text='-', callback_data='-1'),
                      telegram.InlineKeyboardButton(text=f'{quantity}', callback_data='num'),
                      telegram.InlineKeyboardButton(text='+', callback_data='+1')]])
                bot.editMessageReplyMarkup(message_id=inline_message_id, chat_id=inline_chat_id,
                                           reply_markup=inline_keyboard)
                bot.answerCallbackQuery(callback_query_id=query.id, text='با موفقیت اضافه شد', show_alert=False)
            if query['data'] == '-1':
                if quantity != 0:
                    quantity -= 1
                    user_data[f'{food}'] = quantity
                    inline_keyboard = telegram.InlineKeyboardMarkup(
                        [[telegram.InlineKeyboardButton(text='-', callback_data='-1'),
                          telegram.InlineKeyboardButton(text=f'{quantity}', callback_data='num'),
                          telegram.InlineKeyboardButton(text='+', callback_data='+1')]])
                    bot.editMessageReplyMarkup(message_id=inline_message_id, chat_id=inline_chat_id,
                                               reply_markup=inline_keyboard)
                    bot.answerCallbackQuery(callback_query_id=query.id, text='با موفقیت حذف شد', show_alert=False)
            elif query['data'] == 'ok':
                inline_keyboard_address = telegram.InlineKeyboardMarkup(
                    [[telegram.InlineKeyboardButton(text='درب جهاد', callback_data='jahad')],
                     [telegram.InlineKeyboardButton(text='درب انرژی', callback_data='energy')],
                     [telegram.InlineKeyboardButton(text='درب صنایع', callback_data='sanaye')],
                     [telegram.InlineKeyboardButton(text='خوابگاه احمدی روشن', callback_data='ahmadi')],
                     [telegram.InlineKeyboardButton(text='خوابگاه مصلی نژاد', callback_data='mosalanejad')],
                     [telegram.InlineKeyboardButton(text='خوابگاه شادمان', callback_data='shademan')],
                     [telegram.InlineKeyboardButton(text='دانشکده‌ی اقتصاد و مدیریت', callback_data='eghtesad')],
                     [telegram.InlineKeyboardButton(text='BOX', callback_data='BOX')],
                     [telegram.InlineKeyboardButton(text='خوابگاه طرشت ۲ + ۳۰۰۰ تومن هزینه حمل',
                                                    callback_data='tarasht2')],
                     [telegram.InlineKeyboardButton(text='خوابگاه طرشت ۳ + ۳۰۰۰ تومن هزینه حمل',
                                                    callback_data='tarasht3')],
                     [telegram.InlineKeyboardButton(text='خوابگاه شهید شوریده + ۳۰۰۰ تومن هزینه حمل',
                                                    callback_data='shoride')],
                     [telegram.InlineKeyboardButton(text='سایر + ۳۰۰۰ تومن هزینه حمل', callback_data='other')]],
                    resize_keyboard=True)
                bot.sendMessage(chat_id=query['message']['chat']['id'],
                                text='*لطفا آدرس خودت رو انتخاب کن*'
                                , parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=inline_keyboard_address)
                return BotState.CONFIRM

            elif query['data'] == 'cancel':
                user = user_data['user']
                reply_markup = telegram.ReplyKeyboardMarkup(
                    [[telegram.KeyboardButton(text='سفارش')],
                     [telegram.KeyboardButton(text='مشاهده‌ی سبد خرید'),
                      telegram.KeyboardButton(text='خالی کردن سبد خرید')]], resize_keyboard=True)
                bot.sendMessage(chat_id=query['message']['chat']['id'],
                                text="*برای سفارش گزینه‌اش رو انتخاب کن*", reply_markup=reply_markup,
                                parse_mode=telegram.ParseMode.MARKDOWN)

                return ConversationHandler.END

            elif query['data'] == 'detail':
                reply = telegram.ReplyKeyboardRemove()
                bot.sendMessage(chat_id=query['message']['chat']['id'],
                                text="*توضیحات مورد نظرت رو وارد کن*",
                                parse_mode=telegram.ParseMode.MARKDOWN,
                                reply_markup=reply)
                return BotState.DETAIL
            elif query['data'] == 'main' or query['data'] == 'desert':
                user_data['choice'] = query['data']
                return select_food(bot, update, user_data)

        def confirm(bot, update, user_data):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
            django.setup()
            from order.models import Invoice, OrderFood, RestaurantMenu
            user = user_data['user']
            summation = 0
            invoice = Invoice()
            invoice.user = user
            invoice.save()
            for item in user_data:
                if item != 'user' and item != 'restaurant' and item != 'invoice' and item != 'choice' \
                        and user_data[item] != 0 and item != 'detail':
                    order = OrderFood()
                    order.food = RestaurantMenu.objects.get(name=item)
                    order.quantity = user_data[item]
                    summation += order.food.price * order.quantity
                    order.invoice = invoice
                    order.save()
            if update.callback_query:
                query = update.callback_query
                if query['data'] == 'jahad':
                    invoice.address = 'درب جهاد'
                    invoice.amount = summation
                elif query['data'] == 'energy':
                    invoice.address = 'درب انرژی'
                    invoice.amount = summation
                elif query['data'] == 'sanaye':
                    invoice.address = 'درب صنایع'
                    invoice.amount = summation
                elif query['data'] == 'ahmadi':
                    invoice.address = 'خوابگاه احمدی روشن'
                    invoice.amount = summation
                elif query['data'] == 'mosalanejad':
                    invoice.address = 'خوابگاه مصلی نژاد'
                    invoice.amount = summation
                elif query['data'] == 'shademan':
                    invoice.address = 'خوابگاه شادمان'
                    invoice.amount = summation
                elif query['data'] == 'eghtesad':
                    invoice.address = 'دانشکده‌ی اقتصاد و مدیریت'
                    invoice.amount = summation
                elif query['data'] == 'BOX':
                    invoice.address = 'BOX'
                    invoice.amount = summation
                elif query['data'] == 'tarasht2':
                    invoice.address = 'خوابگاه طرشت ۲'
                    invoice.amount = summation + 3000
                elif query['data'] == 'tarasht3':
                    invoice.address = 'خوابگاه طرشت ۳'
                    invoice.amount = summation + 3000
                elif query['data'] == 'shoride':
                    invoice.address = 'خوابگاه شهید شوریده'
                    invoice.amount = summation + 3000
                elif query['data'] == 'other':
                    reply = telegram.ReplyKeyboardRemove()
                    bot.sendMessage(chat_id=query['message']['chat']['id'],
                                    text="*لطفا آدرس رو وارد کن*",
                                    parse_mode=telegram.ParseMode.MARKDOWN,
                                    reply_markup=reply)
                    return BotState.CONFIRM
            else:
                invoice.address = update.message.text
                invoice.amount = summation + 3000
            try:
                invoice.details = user_data['detail']
            except KeyError:
                pass
            invoice.save()
            user_data['invoice'] = invoice
            try:
                invoice = user_data['invoice']
                orders = OrderFood.objects.filter(invoice=invoice)
                text = 'سبد خریدت این اقلام هست:'
                for item in orders:
                    text += '\n ' + item.food.name + '-' + str(item.quantity) + '-' + str(
                        int(item.quantity * item.food.price))

                text += '\n مجموع سفارش:' + '\n' + str(int(invoice.amount))

            except KeyError:
                text = "سبد خریدت خالیه!"

            bot.sendMessage(chat_id=user.chat_id,
                            text=f"*{text}*",
                            parse_mode=telegram.ParseMode.MARKDOWN)

            reply_markup = telegram.InlineKeyboardMarkup(
                [[telegram.InlineKeyboardButton(text='پرداخت نقدی', callback_data='پرداخت نقدی')]])
            bot.sendMessage(chat_id=user.chat_id,
                            text="*لطفا نحوه‌ی پرداختتو انتخاب کن:*",
                            reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
            return BotState.PAYMENT

        def payment(bot, update, user_data):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
            django.setup()
            from order.views.payment import generate_payment_link

            user = user_data['user']
            invoice = user_data['invoice']
            query = update.callback_query
            if query['data'] == 'پرداخت نقدی':
                invoice.is_active = True
                invoice.is_new = True
                invoice.save()
                reply_markup = telegram.InlineKeyboardMarkup(
                    [[telegram.InlineKeyboardButton(text='تایید نهایی', callback_data='تایید نهایی')],
                     [telegram.InlineKeyboardButton(text='انصراف', callback_data='انصراف')]])
                bot.sendMessage(chat_id=user.chat_id,
                                text="*لطفا تایید نهایی رو انجام بده:*",
                                reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
                return BotState.PAYMENT_CONFIRM

            elif query['data'] == 'پرداخت اعتباری':
                link, error = generate_payment_link(user, invoice, 'telegram bot order')
                if not error:
                    text = '*لینک زیر رو انتخاب کن تا به صفحه‌ی پرداخت بری*' + '\n' + link
                    bot.sendMessage(chat_id=user.chat_id,
                                    text=text,
                                    parse_mode=telegram.ParseMode.MARKDOWN)
                    reply_markup = telegram.InlineKeyboardMarkup(
                        [[telegram.InlineKeyboardButton(text='پرداخت کردم', callback_data='پرداخت کردم')],
                         [telegram.InlineKeyboardButton(text='انصراف', callback_data='انصراف')]])
                    bot.sendMessage(chat_id=user.chat_id,
                                    text="*لطفا بعد از پرداخت گزینه‌ی پرداخت کردم رو انتخاب کن:*",
                                    reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
                    return BotState.PAYMENT_CONFIRM

                else:
                    text = '*سایت پرداخت در دسترس نیست لطفا نحوه‌ی پرداخت رو عوض کن*'
                    bot.sendMessage(chat_id=user.chat_id,
                                    text=text,
                                    parse_mode=telegram.ParseMode.MARKDOWN)
                    return BotState.PAYMENT

        def payment_confirm(bot, update, user_data):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
            django.setup()
            user = user_data['user']
            invoice = user_data['invoice']
            query = update.callback_query
            if query['data'] == 'پرداخت کردم':
                if invoice.is_paid:
                    bot.sendMessage(chat_id=user.chat_id,
                                    text=f"*سفارشت برات ارسال می‌شه :) منتظر تماس ما باش*",
                                    parse_mode=telegram.ParseMode.MARKDOWN)
                    reply_markup = telegram.ReplyKeyboardMarkup(
                        [[telegram.KeyboardButton('سفارش')]])
                    bot.sendMessage(chat_id=user.chat_id,
                                    text="*برای سفارش گزینه‌اش رو انتخاب کن*", reply_markup=reply_markup,
                                    parse_mode=telegram.ParseMode.MARKDOWN)
                    return ConversationHandler.END
                else:
                    bot.sendMessage(chat_id=user.chat_id,
                                    text=f"*پرداختت موفقیت آمیز نبوده دوباره تلاش کن*",
                                    parse_mode=telegram.ParseMode.MARKDOWN)
            if query['data'] == 'انصراف' and invoice.is_paid is False:
                invoice.delete()
                user = user_data['user']
                reply_markup = telegram.ReplyKeyboardMarkup(
                    [[telegram.KeyboardButton('سفارش')]])
                bot.sendMessage(chat_id=user.chat_id,
                                text="*برای سفارش گزینه‌اش رو انتخاب کن*", reply_markup=reply_markup,
                                parse_mode=telegram.ParseMode.MARKDOWN)
                return ConversationHandler.END

            if query['data'] == 'انصراف' and invoice.is_paid is True:
                user = user_data['user']
                bot.sendMessage(chat_id=user.chat_id,
                                text="*مبلغ سفارشت پرداخت شده دیگه نمی‌تونی انصراف بدی*",
                                parse_mode=telegram.ParseMode.MARKDOWN)
                bot.sendMessage(chat_id=user.chat_id,
                                text=f"*سفارشت برات ارسال می‌شه :) منتظر تماس ما باش*",
                                parse_mode=telegram.ParseMode.MARKDOWN)
                reply_markup = telegram.ReplyKeyboardMarkup(
                    [[telegram.KeyboardButton(text='سفارش')],
                     [telegram.KeyboardButton(text='مشاهده‌ی سبد خرید'),
                      telegram.KeyboardButton(text='خالی کردن سبد خرید')]], resize_keyboard=True)
                bot.sendMessage(chat_id=user.chat_id,
                                text="*برای سفارش گزینه‌اش رو انتخاب کن*", reply_markup=reply_markup,
                                parse_mode=telegram.ParseMode.MARKDOWN)
                return ConversationHandler.END

            if query['data'] == 'تایید نهایی':
                if invoice.is_active is True and invoice.is_paid is False:
                    bot.sendMessage(chat_id=user.chat_id,
                                    text=f"*سفارشت برات ارسال می‌شه و هزینش{int(invoice.amount)}  تومنه :) منتظر تماس ما باش*",
                                    parse_mode=telegram.ParseMode.MARKDOWN)
                    reply_markup = telegram.ReplyKeyboardMarkup(
                        [[telegram.KeyboardButton('سفارش')]])
                    bot.sendMessage(chat_id=user.chat_id,
                                    text="*برای سفارش گزینه‌اش رو انتخاب کن*", reply_markup=reply_markup,
                                    parse_mode=telegram.ParseMode.MARKDOWN)
                    return ConversationHandler.END

        def sign_up(bot, update):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
            django.setup()
            from order.models import FoodUser
            reply = telegram.ReplyKeyboardRemove
            if not FoodUser.objects.filter(chat_id=update.message.chat_id):
                bot.sendMessage(chat_id=update.message.chat_id,
                                text="*لطفا نام و نام خانوادگیتو وارد کن:*",
                                parse_mode=telegram.ParseMode.MARKDOWN,
                                reply_markup=reply)
            return BotState.SIGNUP_NAME

        def getinfo(bot, update):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
            django.setup()
            from order.models import FoodUser
            user = FoodUser()
            user.name = update.message.text
            user.chat_id = update.message.chat_id
            user.save()
            bot.sendMessage(chat_id=update.message.chat_id,
                            text="*لطفا شماره‌ی تلفن صحیحتو را وارد کن:\n"
                                 "مثال: 09121234567*",
                            parse_mode=telegram.ParseMode.MARKDOWN)
            return BotState.SIGNUP_PHONE

        def phone(bot, update):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
            django.setup()
            from order.models import FoodUser
            user = FoodUser.objects.get(chat_id=update.message.chat_id)
            user.phone = update.message.text
            user.save()
            reply_markup = telegram.ReplyKeyboardMarkup(
                [[telegram.KeyboardButton(text='سفارش')],
                 [telegram.KeyboardButton(text='مشاهده‌ی سبد خرید'),
                  telegram.KeyboardButton(text='خالی کردن سبد خرید')]], resize_keyboard=True)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text="*برای سفارش گزینه‌اش رو انتخاب کن*", reply_markup=reply_markup,
                            parse_mode=telegram.ParseMode.MARKDOWN)
            return BotState.ORDER

        def invalid(bot, update):
            reply_markup = telegram.ReplyKeyboardRemove()
            update.message.reply_text('NotStarted', reply_markup=reply_markup)
            return ConversationHandler.END

        def shop_basket(bot, update, user_data):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reserve_site.settings')
            django.setup()
            from order.models import OrderFood
            try:
                invoice = user_data['invoice']
                orders = OrderFood.objects.filter(invoice=invoice)
                text = 'سبد خریدت این اقلام هست:'
                for item in orders:
                    text += '\n ' + item.food.name + '-' + str(item.quantity) + '-' + str(
                        int(item.quantity * item.food.price))

                text += '\n مجموع سفارش:' + '\n' + str(int(invoice.amount))

            except KeyError:
                text = "سبد خریدت خالیه!"

            bot.sendMessage(chat_id=update.message.chat_id,
                            text=f"*{text}*",
                            parse_mode=telegram.ParseMode.MARKDOWN)

        def empty_basket(bot, update, user_data):
            try:
                user = user_data['user']
            except:
                bot.sendMessage(chat_id=update.message.chat_id,
                                text="*سبد خریدت رو خالی کردم برای سفارش مجدد گزینه‌ی سفارش رو لمس کن*",
                                parse_mode=telegram.ParseMode.MARKDOWN)
                return ConversationHandler.END
            try:
                invoice = user_data['invoice']
                if invoice.is_paid is not True:
                    invoice.delete()
                else:
                    bot.sendMessage(chat_id=user.chat_id,
                                    text="*مبلغ سفارشت پرداخت شده دیگه نمی‌تونی انصراف بدی*",
                                    parse_mode=telegram.ParseMode.MARKDOWN)
            except KeyError:
                pass

            bot.sendMessage(chat_id=update.message.chat_id,
                            text="*سبد خریدت رو خالی کردم برای سفارش مجدد گزینه‌ی سفارش رو لمس کن*",
                            parse_mode=telegram.ParseMode.MARKDOWN)
            return ConversationHandler.END

        def get_detail(bot, update, user_data):
            user_data['detail'] = update.message.text
            inline_keyboard_address = telegram.InlineKeyboardMarkup(
                [[telegram.InlineKeyboardButton(text='درب جهاد', callback_data='jahad')],
                 [telegram.InlineKeyboardButton(text='درب انرژی', callback_data='energy')],
                 [telegram.InlineKeyboardButton(text='درب صنایع', callback_data='sanaye')],
                 [telegram.InlineKeyboardButton(text='خوابگاه احمدی روشن', callback_data='ahmadi')],
                 [telegram.InlineKeyboardButton(text='خوابگاه مصلی نژاد', callback_data='mosalanejad')],
                 [telegram.InlineKeyboardButton(text='خوابگاه شادمان', callback_data='shademan')],
                 [telegram.InlineKeyboardButton(text='دانشکده‌ی اقتصاد و مدیریت', callback_data='eghtesad')],
                 [telegram.InlineKeyboardButton(text='BOX', callback_data='BOX')],
                 [telegram.InlineKeyboardButton(text='خوابگاه طرشت ۲ + ۳۰۰۰ تومن هزینه', callback_data='tarasht2')],
                 [telegram.InlineKeyboardButton(text='خوابگاه طرشت ۳ + ۳۰۰۰ تومن هزینه', callback_data='tarasht3')],
                 [telegram.InlineKeyboardButton(text='خوابگاه شهید شوریده + ۳۰۰۰ تومن هزینه', callback_data='shoride')],
                 [telegram.InlineKeyboardButton(text='سایر + ۳۰۰۰ تومن هزینه', callback_data='other')]],
                resize_keyboard=True)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text='*لطفا آدرس خودت رو انتخاب کن*'
                            , parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=inline_keyboard_address)
            return BotState.CONFIRM

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', callback=start_order, pass_user_data=True),
                          MessageHandler(Filters.regex('سفارش'), callback=start_order, pass_user_data=True)],
            states={
                BotState.INITIALIZE: [MessageHandler(Filters.regex('سفارش'), callback=menu, pass_user_data=True),
                                      MessageHandler(Filters.regex('خالی کردن سبد خرید'), empty_basket,
                                                     pass_user_data=True),
                                      MessageHandler(Filters.regex('مشاهده‌ی سبد خرید'), shop_basket,
                                                     pass_user_data=True)],
                BotState.SIGNUP: [MessageHandler(Filters.regex('ثبت نام'), callback=sign_up)],
                BotState.SIGNUP_NAME: [MessageHandler(Filters.text, callback=getinfo)],
                BotState.SIGNUP_PHONE: [MessageHandler(Filters.text, callback=phone)],
                BotState.ORDER: [MessageHandler(Filters.regex('سفارش'), callback=menu, pass_user_data=True),
                                 MessageHandler(Filters.regex('خالی کردن سبد خرید'), empty_basket, pass_user_data=True),
                                 MessageHandler(Filters.regex('مشاهده‌ی سبد خرید'), shop_basket, pass_user_data=True)],
                BotState.MENU_TYPE: [CallbackQueryHandler(callback=select_food_type, pass_user_data=True),
                                     MessageHandler(Filters.regex('خالی کردن سبد خرید'), empty_basket,
                                                    pass_user_data=True),
                                     MessageHandler(Filters.regex('مشاهده‌ی سبد خرید'), shop_basket,
                                                    pass_user_data=True)
                                     ],
                BotState.MENU: [CallbackQueryHandler(callback=select_food, pass_user_data=True),
                                MessageHandler(Filters.regex('خالی کردن سبد خرید'), empty_basket, pass_user_data=True),
                                MessageHandler(Filters.regex('مشاهده‌ی سبد خرید'), shop_basket, pass_user_data=True)
                                ],
                BotState.EDIT: [CallbackQueryHandler(callback=add_or_remove_item, pass_user_data=True),
                                MessageHandler(Filters.regex('خالی کردن سبد خرید'), empty_basket, pass_user_data=True),
                                MessageHandler(Filters.regex('مشاهده‌ی سبد خرید'), shop_basket, pass_user_data=True)
                                ],
                BotState.CONFIRM: [MessageHandler(Filters.text, callback=confirm, pass_user_data=True),
                                   CallbackQueryHandler(callback=confirm, pass_user_data=True)],
                BotState.PAYMENT: [CallbackQueryHandler(callback=payment, pass_user_data=True),
                                   MessageHandler(Filters.regex('خالی کردن سبد خرید'), empty_basket,
                                                  pass_user_data=True),
                                   MessageHandler(Filters.regex('مشاهده‌ی سبد خرید'), shop_basket, pass_user_data=True)
                                   ],
                BotState.PAYMENT_CONFIRM: [CallbackQueryHandler(callback=payment_confirm, pass_user_data=True),
                                           MessageHandler(Filters.regex('خالی کردن سبد خرید'), empty_basket,
                                                          pass_user_data=True),
                                           MessageHandler(Filters.regex('مشاهده‌ی سبد خرید'), shop_basket,
                                                          pass_user_data=True)
                                           ],
                BotState.DETAIL: [MessageHandler(Filters.text, callback=get_detail, pass_user_data=True)]
            },
            fallbacks=[MessageHandler(Filters.text, callback=invalid)]
        )

        dispatcher.add_handler(conv_handler)

        updater.start_polling()
