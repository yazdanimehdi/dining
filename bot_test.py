import re

import imgkit
import jdatetime
import pandas as pd
import telegram

from dining.models import CustomUser, ReservedTable

user_data = CustomUser.objects.get(username='myjahromi')
date = str(jdatetime.date.today() - jdatetime.timedelta(jdatetime.date.today().weekday()))
date = re.sub(r'\-', '/', date)
last_saturdays_date = list()
last_saturdays_date.append(date)
last_saturdays_date = str(last_saturdays_date)
u = ReservedTable.objects.get(user=user_data, week_start_date=last_saturdays_date)
if user_data.user.chat_id != 0:
    data = {'ناهار': [u.sunday_lunch, u.sunday_lunch, u.monday_lunch,
                      u.tuesday_lunch, u.wednesday_lunch, u.thursday_lunch_self,
                      u.friday_lunch],
            'شام': [u.sunday_dinner, u.sunday_dinner, u.monday_dinner,
                    u.tuesday_dinner, u.wednesday_dinner, u.thursday_dinner,
                    u.friday_dinner]}
    df = pd.DataFrame(data,
                      index=['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه'])

    css = """
     <style type=\"text/css\">
     table {
     color: #333;
     font-family: Helvetica, Arial, sans-serif;
     width: 640px;
     border-collapse:
     collapse; 
     border-spacing: 0;
     }
     td, th {
     border: 1px solid transparent; /* No more visible border */
     height: 30px;
     }
     th {
     background: #DFDFDF; /* Darken header a bit */
     font-weight: bold;
     }
     td {
     background: #FAFAFA;
     text-align: center;
     }
     table tr:nth-child(odd) td{
     background-color: white;
     }
     </style>
     """
    with open('html.html', 'w') as f:
        f.write('')
    text_file = open("html.html", "a")
    text_file.write(css)
    text_file.write(df.to_html())
    text_file.close()
    imgkitoptions = {"format": "png"}
    imgkit.from_file("html.html", 'reserve_img.png', options=imgkitoptions)


    def send_photo(path, chat_id, token):
        bot = telegram.Bot(token=token)
        bot.send_photo(chat_id=chat_id, photo=open(path, 'rb'))


    def send(msg, chat_id, token):
        bot = telegram.Bot(token=token)
        bot.send_message(chat_id=chat_id, text=msg)


    bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'

    message = "سلام\nامروز چهارشنبه‌س و غذاهاتو برات رزرو کردم\nغذاهایی که رزرو کردم ایناست\n"
    send(message, str(user_data.user.chat_id), bot_token)
    send_photo(path='reserve_img.png', chat_id=str(user_data.user.chat_id), token=bot_token)
