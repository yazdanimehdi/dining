from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        import logging

        import telegram
        from dining.bot import start_forget, modify_reserve_end, modify, select_self, select_modify, BotStateModify, \
            select_meal, select_day, reserve, cancel_reserve, modify_reserve, BotStateCharge, BotStateForget, \
            forget_code, start, meal_select, get_phone, payment_result, request_payment, start_reserve, stop_reserve
        from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, ConversationHandler, \
            CallbackQueryHandler

        from dining.models import Merchants
        Merchants.objects.count()

        bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
        updater = Updater(token=bot_token)
        dispatcher = updater.dispatcher
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

        def invalid(bot, update):
            reply_markup = telegram.ReplyKeyboardRemove()
            update.message.reply_text('NotStarted', reply_markup=reply_markup)
            return ConversationHandler.END

        forget_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('کد فراموشی'), callback=start_forget, pass_user_data=True)],
            states={BotStateForget.MEAL: [CallbackQueryHandler(meal_select, pass_user_data=True)],
                    BotStateForget.FORGETCODE: [CallbackQueryHandler(forget_code, pass_user_data=True)]
                    },
            fallbacks=[MessageHandler(Filters.text, callback=invalid)]
        )

        payment_handler = ConversationHandler(
            entry_points=[
                MessageHandler(Filters.regex('افزایش اعتبار'), callback=request_payment, pass_user_data=True)],
            states={BotStateCharge.CHARGE: [CallbackQueryHandler(payment_result, pass_user_data=True)],
                    },
            fallbacks=[MessageHandler(Filters.text, callback=invalid)]
        )

        modify_handler = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('تغییر رزرو'), callback=select_self, pass_user_data=True)],
            states={BotStateModify.SELECTMEAL: [CallbackQueryHandler(select_meal, pass_user_data=True)],
                    BotStateModify.SELECTDAY: [CallbackQueryHandler(select_day, pass_user_data=True)],
                    BotStateModify.SELECT: [CallbackQueryHandler(select_modify, pass_user_data=True)],
                    BotStateModify.SELECTFOOD: [CallbackQueryHandler(modify, pass_user_data=True)],
                    BotStateModify.MODIFY: [CallbackQueryHandler(modify_reserve, pass_user_data=True)],
                    BotStateModify.MODIFYEND: [CallbackQueryHandler(modify_reserve_end, pass_user_data=True)],
                    BotStateModify.RESERVE: [CallbackQueryHandler(reserve, pass_user_data=True)],
                    BotStateModify.CANCEL: [CallbackQueryHandler(cancel_reserve, pass_user_data=True)]},
            fallbacks=[MessageHandler(Filters.text, callback=invalid)]
        )

        start_handler = CommandHandler('start', start)
        contact_handler = MessageHandler(Filters.contact, get_phone)
        stop_handler = MessageHandler(Filters.regex('توقف رزرو'), stop_reserve)
        start_reserve_handler = MessageHandler(Filters.regex('شروع رزرو'), start_reserve)
        dispatcher.add_handler(forget_handler)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(contact_handler)
        dispatcher.add_handler(stop_handler)
        dispatcher.add_handler(start_reserve_handler)
        dispatcher.add_handler(payment_handler)
        dispatcher.add_handler(modify_handler)
        updater.start_polling()
