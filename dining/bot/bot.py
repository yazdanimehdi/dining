import logging

import telegram
from forgetting_code import meal_select, forget_code, start_forget, BotStateForget
from modify import modify, modify_reserve, cancel_reserve, reserve, modify_reserve_end, select_day, \
    select_meal, select_modify, select_self, BotStateModify
from payment_sharif import payment_result, request_payment, BotStateCharge
from reserve_set_bot import start, get_phone
from stop_start_reserve import stop_reserve, start_reserve
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, ConversationHandler, CallbackQueryHandler

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
    entry_points=[MessageHandler(Filters.regex('افزایش اعتبار'), callback=request_payment, pass_user_data=True)],
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
