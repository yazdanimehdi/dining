import random
import re
import time

import jdatetime
import requests
from bs4 import BeautifulSoup
from celery import task
from lxml import html


@task
def get_reserved_sharif():
    from dining.models import UserDiningData, ReservedTable
    for user_data in UserDiningData.objects.filter(university__tag='sharif'):
        if user_data.user.is_paid:
            try:
                time.sleep(random.Random.randint(2, 5))
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

                date = str(jdatetime.date.today() - jdatetime.timedelta(jdatetime.date.today().weekday()))
                date = re.sub(r'\-', '/', date)
                last_saturdays_date = list()
                last_saturdays_date.append(date)
                last_saturdays_date = str(last_saturdays_date)

                filter = ReservedTable.objects.filter(user=user_data.user, week_start_date=last_saturdays_date)

                next_week_reserved_table = {
                    'week': '0',
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

                if not filter:
                    reserved = ReservedTable()
                    reserved.user = user_data.user

                    reserved.week_start_date = last_saturdays_date

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


            except Exception as e:
                print(e)
