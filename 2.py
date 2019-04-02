import re

import imgkit
import jdatetime
import pandas as pd
import requests
import telegram
from bs4 import BeautifulSoup
from lxml import html

from dining.models import UserDiningData, UserSelfs, UserPreferableFood, ReservedTable


def login(user_data):
    login_url = user_data.university.login_url
    session_requests = requests.session()
    result = session_requests.get(login_url)
    csrf = user_data.university.csrf_name
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath(f"//input[@name='{csrf}']/@value")))[0]
    payload = {
        user_data.university.form_username: user_data.dining_username,
        user_data.university.form_password: user_data.dining_password,
        user_data.university.csrf_name: authenticity_token,
    }
    result = session_requests.post(login_url, data=payload, headers=dict(referer=login_url))
    if 'login' not in result.url:
        return session_requests.cookies
    else:
        raise ValueError


def get_user_id(cookie):
    reserve_url = 'http://dining.sharif.ir/admin/food/food-reserve/reserve'
    session_requests = requests.session()
    session_requests.cookies = cookie
    result = session_requests.get(reserve_url)
    soup = BeautifulSoup(result.content, 'html.parser')

    try:
        button = soup.find_all('button', class_="btn btn-default navigation-link")[0].get('onclick')
        return button.split(';')[0].split(',')[4][:-1]
    except IndexError:
        raise ValueError


def get_next_week_dishes(user_data, cookie, self_id, user_id):
    from dining.models import Food, UserPreferableFood

    session_requests = requests.session()
    session_requests.cookies = cookie

    next_week = {
        'id': 0,
        'parent_id': self_id,
        'week': 1,
        'user_id': user_id
    }

    load_reserve_table = 'http://dining.sharif.ir/admin/food/food-reserve/load-reserve-table'

    result = session_requests.post(load_reserve_table, data=next_week)

    soup = BeautifulSoup(result.content, 'html.parser')

    table_rows = soup.find_all('tr')[1:]

    data_lunch = dict()
    data_dinner = dict()
    for row in table_rows:
        day = re.findall(r'<th>\s+(.*?)\s\s', str(row))[0]
        lunch = row.find_all('td')[0].find_all('div')
        dishes = list()
        for dish in lunch:
            try:
                food_name = dish.text.split('(')[0].strip()
                food_id = dish.find('span').get('onclick').split('do_reserve_from_diet(')[1].split(',')[0].strip('\"')
                query = Food.objects.filter(name__icontains=food_name, university=user_data.university)
                if query:
                    dishes.append((query[0].name, food_id))
                else:
                    new_food = Food()
                    new_food.name = food_name
                    new_food.id = food_id
                    new_food.save()
                    dishes.append((food_name, food_id))
                    preferred_food_object = UserPreferableFood
                    preferred_food_object.user = user_data.user
                    preferred_food_object.food = new_food
                    preferred_food_object.score = 5
                    preferred_food_object.save()

            except:
                pass
        data_lunch[day] = dishes

        dinner = row.find_all('td')[1].find_all('div')
        dishes = list()
        for dish in dinner:
            try:
                food_name = dish.text.split('(')[0].strip()
                food_id = dish.find('span').get('onclick').split('do_reserve_from_diet(')[1].split(',')[0].strip('\"')
                query = Food.objects.filter(name__icontains=food_name, university=user_data.university)
                if query:
                    dishes.append((query[0].name, food_id))
                else:
                    new_food = Food()
                    new_food.name = food_name
                    new_food.id = food_id
                    new_food.save()
                    dishes.append((food_name, food_id))
                    preferred_food_object = UserPreferableFood
                    preferred_food_object.user = user_data.user
                    preferred_food_object.food = new_food
                    preferred_food_object.score = 5
                    preferred_food_object.save()

            except:
                pass

        data_dinner[day] = dishes

    return data_lunch, data_dinner


def save_values(user_data, data_lunch, data_dinner, self_id):
    from dining.models import Dicty, Key, Val

    try:
        dictionary_model = Dicty.objects.get(name=user_data.user.username + 'data_lunch' + f'{self_id}')
        Key.objects.filter(container__name=user_data.user.username + 'data_lunch').delete()


    except:
        dictionary_model = Dicty()
        dictionary_model.name = user_data.user.username + 'data_lunch' + f'{self_id}'
        dictionary_model.save()

    for item in data_dinner:
        key = Key()
        key.container = dictionary_model
        key.key = item[0]
        key.save()
        for food in data_dinner[item]:
            value = Val()
            value.key = key
            value.container = dictionary_model
            value.name = food[0]
            value.food_id = food[1]
            value.save()
    try:
        dictionary_model = Dicty.objects.get(name=user_data.user.username + 'data_dinner' + f'{self_id}')
        Key.objects.filter(container__name=user_data.user.username + 'data_dinner').delete()

    except:
        dictionary_model = Dicty()
        dictionary_model.name = user_data.user.username + 'data_dinner' + f'{self_id}'
        dictionary_model.save()

    for item in data_lunch:
        key = Key()
        key.container = dictionary_model
        key.key = item[0]
        key.save()
        for food in data_lunch[item]:
            value = Val()
            value.key = key
            value.container = dictionary_model
            value.name = food[0]
            value.food_id = food[1]
            value.save()


def do_reserve(food_id, self_id, user_id, cookie):
    food_reserve_request = {
        'id': food_id,
        'place_id': self_id,
        'food_place_id': '0',
        'self_id': self_id,
        'user_id': user_id
    }
    session_requests = requests.session()
    session_requests.cookies = cookie
    session_requests.post('https://dining.sharif.ir/admin/food/food-reserve/do-reserve-from-diet?user_id=' + user_id,
                          data=food_reserve_request, verify=False)


def get_reserved_table(user_data, user_id, cookie):
    session_requests = requests.session()
    session_requests.cookies = cookie
    next_week_reserved_table = {
        'week': '1',
        'user_id': user_id
    }
    url_reserved_table = user_data.university.reserved_table
    result = session_requests.post(url_reserved_table, data=next_week_reserved_table)
    soup = BeautifulSoup(result.content, 'html.parser')

    table_rows = soup.find_all('tr')[1:]

    data_lunch = dict()
    data_dinner = dict()
    for row in table_rows:
        day = re.findall(r'<th>\s+(.*?)\s\s', str(row))[0]
        lunch = row.find_all('td')[0].find_all('div')
        dishes = list()
        for dish in lunch:
            try:
                food_name = dish.text.split('(')[0].strip()
                dishes.append(food_name)
            except:
                dishes.append('-')
        data_lunch[day] = dishes

        dinner = row.find_all('td')[1].find_all('div')
        dishes = list()
        for dish in dinner:
            try:
                food_name = dish.text.split('(')[0].strip()
                dishes.append(food_name)
            except:
                dishes.append('-')

        data_dinner[day] = dishes

    result = session_requests.get('http://dining.sharif.ir/admin/payment/payment/charge')
    soup = BeautifulSoup(result.text, 'html.parser')
    soup_find = soup.find_all('h4', {'class': 'control-label'})
    credit_raw = soup_find[0].find_all('span', {'dir': 'ltr'})[0].text.strip()
    credit = float(re.sub(',', '.', credit_raw))

    return data_lunch, data_dinner, credit


def telegram_table_message(user_data, data_lunch, data_dinner):
    if user_data.user.chat_id != 0:
        data = {'ناهار': [data_lunch['شنبه'], data_lunch['یک شنبه'], data_lunch['دوشنبه'],
                          data_lunch['سه شنبه'], data_lunch['چهارشنبه'], data_lunch['پنج شنبه'],
                          data_lunch['جمعه']],
                'شام': [data_dinner['شنبه'], data_dinner['یک شنبه'], data_dinner['دوشنبه'],
                        data_dinner['سه شنبه'], data_dinner['چهارشنبه'], data_dinner['پنج شنبه'],
                        data_dinner['جمعه']]}
        df = pd.DataFrame(data,
                          index=['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه'])

        css = """
        <!DOCTYPE html>
        <head>
            <meta charset="UTF-8">
        </head>
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

        def send(msg, chat_id, token, keyboard):
            bot = telegram.Bot(token=token)
            bot.send_message(chat_id=chat_id, text=msg, reply_markup=keyboard)

        bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
        message = "سلام\nامروز چهارشنبه‌ئ و غذاهاتو برات رزرو کردم\nغذاهایی که رزرو کردم ایناست\
        nبرای تغییر در رزرو گزینه‌ي زیر رو لمس کن"
        reply_markup = telegram.ReplyKeyboardMarkup(
            [[telegram.KeyboardButton('تغییر رزرو')]], one_time_keyboard=False)
        send(message, str(user_data.user.chat_id), bot_token, reply_markup)
        send_photo(path='reserve_img.png',
                   chat_id=str(user_data.user.chat_id),
                   token=bot_token)


for user_data in UserDiningData.objects.filter(university__tag='sharif'):
    if user_data.user.is_paid is True and user_data.user.reserve is True:

        active_selfs = UserSelfs.objects.filter(user=user_data.user, is_active=True)
        try:
            cookie = login(user_data)
        except ValueError:
            continue
        user_id = get_user_id(cookie)

        for self in active_selfs:

            data_lunch, data_dinner = get_next_week_dishes(user_data, cookie, self.self_id, user_id)
            save_values(user_data, data_lunch, data_dinner, self.self_id)

            chosen_days_lunch = []

            if user_data.reserve_friday_lunch:
                chosen_days_lunch.append('جمعه')
            if user_data.reserve_saturday_lunch:
                chosen_days_lunch.append('شنبه')
            if user_data.reserve_sunday_lunch:
                chosen_days_lunch.append('یک شنبه')
            if user_data.reserve_monday_lunch:
                chosen_days_lunch.append('دوشنبه')
            if user_data.reserve_tuesday_lunch:
                chosen_days_lunch.append('سه شنبه')
            if user_data.reserve_wednesday_lunch:
                chosen_days_lunch.append('چهارشنبه')
            if user_data.reserve_thursday_lunch:
                chosen_days_lunch.append('پنج شنبه')

            chosen_days_dinner = []

            if user_data.reserve_friday_dinner:
                chosen_days_dinner.append('جمعه')
            if user_data.reserve_saturday_dinner:
                chosen_days_dinner.append('شنبه')
            if user_data.reserve_sunday_dinner:
                chosen_days_dinner.append('یک شنبه')
            if user_data.reserve_monday_dinner:
                chosen_days_dinner.append('دوشنبه')
            if user_data.reserve_tuesday_dinner:
                chosen_days_dinner.append('سه شنبه')
            if user_data.reserve_wednesday_lunch:
                chosen_days_dinner.append('چهارشنبه')
            if user_data.reserve_thursday_dinner:
                chosen_days_dinner.append('پنج شنبه')

            for day in chosen_days_lunch:
                preferred_foods = []
                for dish in data_lunch[day]:
                    preferred_foods.append((dish[1], UserPreferableFood.objects.filter(
                        food__name=dish[0])[0].score))
                preferred_foods.sort(key=lambda x: x[1], reverse=True)
                if preferred_foods:
                    do_reserve(preferred_foods[0][0], user_id, self.self_id, cookie)

            for day in chosen_days_dinner:
                preferred_foods = []
                for dish in data_dinner[day]:
                    preferred_foods.append((dish[1], UserPreferableFood.objects.filter(
                        food__name=dish[0])[0].score))
                preferred_foods.sort(key=lambda x: x[1], reverse=True)
                if preferred_foods:
                    do_reserve(preferred_foods[0][0], user_id, self.self_id, cookie)

        data_lunch, data_dinner, credit = get_reserved_table(user_data, user_id, cookie)

        date = str(jdatetime.date.today() + jdatetime.timedelta(3))
        date = re.sub(r'\-', '/', date)
        saturdays_date = list()
        saturdays_date.append(date)
        saturdays_date = str(saturdays_date)

        filter = ReservedTable.objects.filter(user=user_data.user, week_start_date=saturdays_date)
        flag = True
        if not filter:
            reserved = ReservedTable()
            reserved.user = user_data.user

            reserved.week_start_date = saturdays_date

            reserved.friday_lunch = data_lunch['جمعه']
            reserved.saturday_lunch = data_lunch['شنبه']
            reserved.sunday_lunch = data_lunch['یک شنبه']
            reserved.monday_lunch = data_lunch['دوشنبه']
            reserved.tuesday_lunch = data_lunch['سه شنبه']
            reserved.wednesday_lunch = data_lunch['چهارشنبه']
            reserved.thursday_lunch = data_lunch['پنج شنبه']

            reserved.friday_dinner = data_dinner['جمعه']
            reserved.saturday_dinner = data_dinner['شنبه']
            reserved.sunday_dinner = data_dinner['یک شنبه']
            reserved.monday_dinner = data_dinner['دوشنبه']
            reserved.tuesday_dinner = data_dinner['سه شنبه']
            reserved.wednesday_dinner = data_dinner['چهارشنبه']
            reserved.thursday_dinner = data_dinner['پنج شنبه']

            reserved.credit = credit

            reserved.save()

        else:
            flag = False
            filter[0].friday_lunch = data_lunch['جمعه']
            filter[0].saturday_lunch = data_lunch['شنبه']
            filter[0].sunday_lunch = data_lunch['یک شنبه']
            filter[0].monday_lunch = data_lunch['دوشنبه']
            filter[0].tuesday_lunch = data_lunch['سه شنبه']
            filter[0].wednesday_lunch = data_lunch['چهارشنبه']
            filter[0].thursday_lunch = data_lunch['پنج شنبه']

            filter[0].friday_dinner = data_dinner['جمعه']
            filter[0].saturday_dinner = data_dinner['شنبه']
            filter[0].sunday_dinner = data_dinner['یک شنبه']
            filter[0].monday_dinner = data_dinner['دوشنبه']
            filter[0].tuesday_dinner = data_dinner['سه شنبه']
            filter[0].wednesday_dinner = data_dinner['چهارشنبه']
            filter[0].thursday_dinner = data_dinner['پنج شنبه']

            filter[0].credit = credit

            filter[0].save()

        if flag:
            try:
                telegram_table_message(user_data, data_lunch, data_dinner)
            except:
                continue
