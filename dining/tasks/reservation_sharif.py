import re

import imgkit
import jdatetime
import pandas as pd
import requests
import telegram
from bs4 import BeautifulSoup
from celery import task
from lxml import html


@task()
def reserve_function():
    from dining.models import UserDiningData, ReservedTable, UserSelfs, UserPreferableFood, Food, Dicty, Key, Val

    for user_data in UserDiningData.objects.filter(university__tag='sharif'):
        if user_data.user.is_paid == True and user_data.user.reserve == True:
            try:
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
                result = session_requests.get(user_data.university.reserve_table)
                regex_find = re.findall(r'load_diet_reserve_table\((.*)\);\">هفته بعد', result.text)
                if regex_find:
                    user_id = re.findall(r'\,(\d\d+)', regex_find[0])[0]
                else:
                    continue
                url_next_week = user_data.university.url_next_week
                for self in UserSelfs.objects.filter(user=user_data.user, is_active=True):
                    next_week_payload = {
                        'id': '0',
                        'parent_id': self.self_id,
                        'week': '1',
                        'user_id': user_id
                    }
                    result = session_requests.post(url_next_week, data=next_week_payload)

                    # mining main table

                    soup = BeautifulSoup(result.text, 'html.parser')
                    soup_find = soup.find_all('tr')
                    soup_find.pop(0)

                    data_lunch = dict()
                    data_dinner = dict()
                    for row in soup_find:
                        day = re.findall(r'<th>\s+(.*?)\s\s', str(row))
                        date = re.findall(r'<br\/>\s+(.+?)\s+', str(row))
                        food_id_lunch = re.findall(r'do_reserve_from_diet\(\"(\d+)\"', str(row.find_all('td')[0]))
                        food_names_lunch = re.findall(
                            r'style=\"color:blue;\"><\/span>(.+?)\s<span class=\"price-span\">',
                            str(row.find_all('td')[0]))
                        food_id_dinner = re.findall(r'do_reserve_from_diet\(\"(\d+)\"', str(row.find_all('td')[1]))
                        food_names_dinner = re.findall(
                            r'style=\"color:blue;\"><\/span>(.+?)\s<span class=\"price-span\">',
                            str(row.find_all('td')[1]))
                        i = 0
                        foods = []
                        if not food_id_dinner:
                            food_id_dinner = ['-', '-', '-', '-']
                        for food in food_names_dinner:
                            if '<span class="label label-warning food_reserve_label">(نیمه تعطیل)</span>' in food:
                                food = \
                                    food.split(
                                        '<span class="label label-warning food_reserve_label">(نیمه تعطیل)</span>')[
                                        0].strip()
                            flag = False
                            for db_food in UserPreferableFood.objects.filter(user=user_data.user):
                                if set(db_food.food.name.split(' ')).issubset(food.split(' ')):
                                    food = db_food.food.name
                                    flag = True
                                elif db_food.food.name in food:
                                    food = db_food.food.name
                                    flag = True
                            if flag:
                                foods.append((food_id_dinner[i], food))
                            else:
                                newfood = Food()
                                newfood.name = food
                                newfood.university = user_data.university
                                newfood.save()
                                u = UserPreferableFood()
                                u.user = user_data.user
                                u.food = newfood
                                u.score = 0
                                u.save()
                            i += 1
                        data_dinner[(day[0], date[0])] = foods
                        i = 0
                        foods = []
                        if not food_id_lunch:
                            food_id_lunch = ['-', '-', '-']
                        for food in food_names_lunch:
                            if '<span class="label label-warning food_reserve_label">(نیمه تعطیل)</span>' in food:
                                food = \
                                    food.split(
                                        '<span class="label label-warning food_reserve_label">(نیمه تعطیل)</span>')[
                                        0].strip()
                            flag = False
                            for db_food in UserPreferableFood.objects.filter(user=user_data.user):
                                if (set(db_food.food.name.split(' ')).issubset(food.split(' '))) or (
                                        db_food.food.name in food):
                                    food = db_food.food.name
                                    flag = True
                            if flag:
                                foods.append((food_id_lunch[i], food))
                            else:
                                newfood = Food()
                                newfood.name = food
                                newfood.university = user_data.university
                                newfood.id = 0
                                newfood.save()
                                u = UserPreferableFood()
                                u.user = user_data.user
                                u.food = newfood
                                u.score = 0
                                u.save()

                            i += 1
                        data_lunch[(day[0], date[0])] = foods

                    dictionary_model = Dicty.objects.get_or_create(name=user_data.user.username + 'data_dinner')

                    Key.objects.filter(container__name=user_data.user.username + 'data_dinner').delete()
                    for item in data_dinner:
                        key = Key()
                        key.container = dictionary_model[0]
                        key.key = item[0]
                        key.save()
                        for food in data_dinner[item]:
                            value = Val()
                            value.key = key
                            value.container = dictionary_model[0]
                            value.name = food[1]
                            value.food_id = food[0]
                            value.save()

                    dictionary_model = Dicty.objects.get_or_create(name=user_data.user.username + 'data_dinner')

                    Key.objects.filter(container__name=user_data.user.username).delete()
                    for item in data_lunch:
                        key = Key()
                        key.container = dictionary_model[0]
                        key.key = item[0]
                        key.save()
                        for food in data_lunch[item]:
                            value = Val()
                            value.key = key
                            value.container = dictionary_model[0]
                            value.name = food[1]
                            value.food_id = food[0]
                            value.save()

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

                    for item in data_lunch:
                        for day in chosen_days_lunch:
                            if item[0] == day and (data_lunch[item] is not None):
                                food_list = []
                                for food in data_lunch[item]:
                                    food_list.append(
                                        (food[0],
                                         UserPreferableFood.objects.filter(user=user_data.user, food__name=food[1])[0]))
                                food_list.sort(key=lambda x: x[1].score, reverse=True)
                                prefered_data = food_list
                                if prefered_data:
                                    if prefered_data[0][0] != '-' and prefered_data[0][0] != '':
                                        food_reserve_request = {
                                            'id': prefered_data[0][0],
                                            'place_id': self.self_id,
                                            'food_place_id': '0',
                                            'self_id': self.self_id,
                                            'user_id': user_id
                                        }

                                        session_requests.post(user_data.university.reserve_url + user_id,
                                                              data=food_reserve_request)

                    for item in data_dinner:
                        if data_dinner[item]:
                            for day in chosen_days_dinner:
                                if item[0] == day and (data_dinner[item] is not None):
                                    food_list = []
                                    for food in data_dinner[item]:
                                        food_list.append(
                                            (food[0],
                                             UserPreferableFood.objects.filter(user=user_data.user, food__name=food[1])[
                                                 0]))
                                    food_list.sort(key=lambda x: x[1].score, reverse=True)
                                    prefered_data = food_list
                                    if prefered_data:
                                        if prefered_data[0][0] != '-' and prefered_data[0][0] != '':
                                            food_reserve_request = {
                                                'id': prefered_data[0][0],
                                                'place_id': self.self_id,
                                                'food_place_id': '0',
                                                'self_id': self.self_id,
                                                'user_id': user_id
                                            }

                                            session_requests.post(user_data.university.reserve_url + user_id,
                                                                  data=food_reserve_request)

                date = str(jdatetime.date.today() + jdatetime.timedelta(2))
                date = re.sub(r'\-', '/', date)
                saturdays_date = list()
                saturdays_date.append(date)
                saturdays_date = str(saturdays_date)

                filter = ReservedTable.objects.filter(user=user_data.user, week_start_date=saturdays_date)

                next_week_reserved_table = {
                    'week': '1',
                    'user_id': user_id
                }
                url_reserved_table = user_data.university.reserved_table
                result = session_requests.post(url_reserved_table, data=next_week_reserved_table)

                soup = BeautifulSoup(result.text, 'html.parser')
                soup_find = soup.find_all('tr')
                soup_find.pop(0)

                data_lunch = dict()
                data_dinner = dict()
                for row in soup_find:
                    day = re.findall(r'<th>\s+(.*?)\s\s', str(row))
                    food_names_lunch = re.findall(r'<span>(.+?)<\/span>', str(row.find_all('td')[0]))
                    food_names_dinner = re.findall(r'<span>(.+?)<\/span>', str(row.find_all('td')[1]))
                    i = 0
                    foods = []
                    if food_names_dinner:
                        for food in food_names_dinner:
                            if '<span class="label label-warning food_reserve_label">(نیمه تعطیل)</span>' in food:
                                food = \
                                    food.split(
                                        '<span class="label label-warning food_reserve_label">(نیمه تعطیل)</span>')[
                                        0].strip()
                            foods.append(food)
                            i += 1
                        data_dinner[day[0]] = foods
                    else:
                        data_dinner[day[0]] = '-'

                    i = 0
                    foods = []
                    if food_names_lunch:
                        for food in food_names_lunch:
                            if '<span class="label label-warning food_reserve_label">(نیمه تعطیل)</span>' in food:
                                food = \
                                    food.split(
                                        '<span class="label label-warning food_reserve_label">(نیمه تعطیل)</span>')[
                                        0].strip()
                            foods.append(food)
                            i += 1
                        data_lunch[day[0]] = foods
                    else:
                        data_lunch[day[0]] = '-'

                    result = session_requests.get('http://dining.sharif.ir/admin/payment/payment/charge')
                    soup = BeautifulSoup(result.text, 'html.parser')
                    soup_find = soup.find_all('h4', {'class': 'control-label'})
                    credit_raw = soup_find[0].find_all('span', {'dir': 'ltr'})[0].text.strip()
                    credit = float(re.sub(',', '.', credit_raw))
                flag = False
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

                    flag = True
                else:

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

                    def send(msg, chat_id, token):
                        bot = telegram.Bot(token=token)
                        bot.send_message(chat_id=chat_id, text=msg)

                    bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
                    if flag == True:
                        message = "سلام\nامروز پنج‌شنبه‌س و غذاهاتو برات رزرو کردم\nغذاهایی که رزرو کردم ایناست\n"
                        send(message, str(user_data.user.chat_id), bot_token)
                        send_photo(path='reserve_img.png', chat_id=str(user_data.user.chat_id), token=bot_token)

            except Exception as e:
                print(e)
