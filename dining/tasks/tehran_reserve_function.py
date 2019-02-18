import re
import time

import imgkit
import jdatetime
import pandas as pd
import requests
import telegram
from bs4 import BeautifulSoup
from celery import task
from django.db.models import Q
from lxml import html


@task()
def tehran_reserve_function():
    from dining.models import UserDiningData, ReservedTable, UserSelfs, UserPreferableFood, SamadPrefrredDays, Food, \
        University

    for user_data in UserDiningData.objects.filter(university__name='دانشگاه تهران'):
        if user_data.user.is_paid:
            r = 0
            while r < 5:
                try:
                    login_url = 'https://auth4.ut.ac.ir:8443/cas/login?service=https://dining1.ut.ac.ir/login/cas'
                    reserve_get_url = 'https://dining1.ut.ac.ir/nurture/user/multi/reserve/reserve.rose'
                    session_requests = requests.session()
                    result = session_requests.get(login_url, verify=False)
                    tree = html.fromstring(result.text)
                    authenticity_token_execution = list(set(tree.xpath("//input[@name='execution']/@value")))[0]
                    authenticity_token_lt = list(set(tree.xpath("//input[@name='lt']/@value")))[0]

                    payload = {
                        'username': user_data.dining_username,
                        'password': user_data.dining_password,
                        'lt': authenticity_token_lt,
                        'execution': authenticity_token_execution,
                        '_eventId': 'submit'

                    }
                    result = session_requests.post(login_url, data=payload, headers=dict(referer=login_url),
                                                   verify=False)
                    tree = html.fromstring(result.text)
                    result = session_requests.get(reserve_get_url, verify=False)
                    if result.status_code == 403:
                        link = list(set(tree.xpath("//*[@id=\"cas_username\"]/option[2]/@value")))[0]
                        result = session_requests.get('https://dining1.ut.ac.ir' + link, verify=False)
                    result = session_requests.get(reserve_get_url, verify=False)
                    tree = html.fromstring(result.text)
                    authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
                    weekStartDateTime = list(set(tree.xpath("//input[@name='weekStartDateTime']/@value")))[0]
                    weekStartDateTimeAjx = list(set(tree.xpath("//input[@name='weekStartDateTimeAjx']/@value")))[0]
                    remainCredit = list(set(tree.xpath("//input[@name='remainCredit']/@value")))[0]

                    for self in UserSelfs.objects.filter(user=user_data.user, is_active=True):
                        payload_load = {
                            'method:showNextWeek': 'Submit',
                            'weekStartDateTime': weekStartDateTime,
                            'remainCredit': remainCredit,
                            'selfChangeReserveId': '',
                            'weekStartDateTimeAjx': weekStartDateTimeAjx,
                            'selectedSelfDefId': self.self_id,
                            '_csrf': authenticity_token,
                        }
                        result = session_requests.post(reserve_get_url, data=payload_load)
                        tree = html.fromstring(result.text)
                        soup = BeautifulSoup(result.text, 'html.parser')
                        soup_find = soup.findAll('tr')[2].findAll('tr')
                        i = 0
                        a_index = list()
                        for tr in soup_find:
                            a = re.findall(r'شنبه', str(tr))
                            if a:
                                a_index.append(i)
                            i += 1
                        lunch_data = dict()
                        breakfast_data = dict()
                        dinner_data = dict()
                        j = 0
                        for i in a_index:
                            day = re.findall(
                                r'align=\"center\" style=\"background:#F0F0F0;border:1px solid #CCCCCC; border-top:none;\" valign=\"middle\" width=\"12%\">\s+(.*)\s+<br\/>',
                                str(soup_find[i]))[0].strip()
                            date = re.findall(r'<div>(.+)</div>', str(soup_find[i]))[0]
                            weekStartDateTime = \
                                list(set(tree.xpath("//*[@id=\"resFinalform_weekStartDateTime\"]/@value")))[
                                    0]
                            weekStartDateTimeAjx = \
                                list(set(tree.xpath("//input[@name='weekStartDateTimeAjx']/@value")))[0]
                            foods_lunch = []
                            foods_dinner = []
                            foods_breakfast = []
                            for soupf in soup_find[i].find_all('tr'):
                                price_list = re.findall(r'class=\"xstooltip\".+\>\s+(.+)', str(soupf))[0]
                                programId = re.findall(r'programId\" type=\"hidden\" value=\"(.+)\"', str(soupf))[0]
                                mealTypeId = re.findall(r'mealTypeId\" type=\"hidden\" value=\"(.+)\"', str(soupf))[0]
                                programDateTime = \
                                    re.findall(r'programDateTime\" type=\"hidden\" value=\"(.+)\"', str(soupf))[0]
                                foodTypeId = re.findall(r'foodTypeId\"\s+.+value=\"(.+)\"',
                                                        str(soupf))[0]
                                freeFoodSelected = \
                                    re.findall(r'freeFoodSelected\" type=\"hidden\" value="(.+)\"', str(soupf))[
                                        0]
                                food_name = re.findall(r'xstooltip_hide\(\'foodPriceTooltip.+\s+(.+)', str(soupf))
                                if food_name:
                                    food_name = food_name[0].split('|')[1].strip()

                                if tree.xpath(f"//*[@id=\"userWeekReserves.selected{j}_hidden\"]/@value"):
                                    selected = tree.xpath(f"//*[@id=\"userWeekReserves.selected{j}_hidden\"]/@value")[0]
                                else:
                                    if 'null' in tree.xpath(f'//*[@id=\"userWeekReserves.selected{j}\"]/@onclick')[0]:
                                        selected = 'false'
                                    else:
                                        selected = 'true'
                                if selected == 'true':
                                    selected_count = 1
                                else:
                                    selected_count = 0
                                flag = False
                                for db_food in Food.objects.filter(university=user_data.university):
                                    if set(db_food.name.split(' ')).issubset(food_name.split(' ')):
                                        flag = True
                                    elif db_food.name in food_name:
                                        flag = True
                                if not flag:
                                    uni = University.objects.get(name=user_data.university)
                                    newfood = Food()
                                    newfood.name = food_name
                                    newfood.university = uni
                                    newfood.save()
                                    u = UserPreferableFood.objects.create(user=user_data.user, food=newfood, score=5)
                                    u.save()
                                    flag = True

                                print(flag)
                                if mealTypeId == '1':
                                    foods_breakfast.append(
                                        (j, food_name, price_list, programId, mealTypeId, programDateTime,
                                         foodTypeId, freeFoodSelected, selected, selected_count))
                                if mealTypeId == '2':
                                    foods_lunch.append(
                                        (j, food_name, price_list, programId, mealTypeId, programDateTime,
                                         foodTypeId, freeFoodSelected, selected, selected_count))
                                if mealTypeId == '3':
                                    foods_dinner.append(
                                        (j, food_name, price_list, programId, mealTypeId, programDateTime,
                                         foodTypeId, freeFoodSelected, selected, selected_count))
                                j += 1

                            lunch_data[(day, date)] = foods_lunch
                            dinner_data[(day, date)] = foods_dinner
                            breakfast_data[(day, date)] = foods_breakfast
                            Credit = int(list(set(tree.xpath("//input[@name='remainCredit']/@value")))[0])
                        payload_reserve = {
                            'weekStartDateTime': weekStartDateTime,
                            'method:doReserve': 'Submit',
                            'selfChangeReserveId': '',
                            'weekStartDateTimeAjx': weekStartDateTimeAjx,
                            'selectedSelfDefId': self.self_id,
                            '_csrf': authenticity_token,
                        }

                        pdays = SamadPrefrredDays.objects.get(user=user_data.user, active_self=self)

                        chosen_days_breakfast = []
                        if pdays.reserve_friday_breakfast:
                            chosen_days_breakfast.append('جمعه')
                        if pdays.reserve_saturday_breakfast:
                            chosen_days_breakfast.append('شنبه')
                        if pdays.reserve_sunday_breakfast:
                            chosen_days_breakfast.append('یکشنبه')
                        if pdays.reserve_monday_breakfast:
                            chosen_days_breakfast.append('دوشنبه')
                        if pdays.reserve_tuesday_breakfast:
                            chosen_days_breakfast.append('سه شنبه')
                        if pdays.reserve_wednesday_breakfast:
                            chosen_days_breakfast.append('چهارشنبه')
                        if pdays.reserve_thursday_breakfast:
                            chosen_days_breakfast.append('پنجشنبه')

                        chosen_days_lunch = []

                        if pdays.reserve_friday_lunch:
                            chosen_days_lunch.append('جمعه')
                        if pdays.reserve_saturday_lunch:
                            chosen_days_lunch.append('شنبه')
                        if pdays.reserve_sunday_lunch:
                            chosen_days_lunch.append('یکشنبه')
                        if pdays.reserve_monday_lunch:
                            chosen_days_lunch.append('دوشنبه')
                        if pdays.reserve_tuesday_lunch:
                            chosen_days_lunch.append('سه شنبه')
                        if pdays.reserve_wednesday_lunch:
                            chosen_days_lunch.append('چهارشنبه')
                        if pdays.reserve_thursday_lunch:
                            chosen_days_lunch.append('پنجشنبه')

                        chosen_days_dinner = []

                        if pdays.reserve_friday_dinner:
                            chosen_days_dinner.append('جمعه')
                        if pdays.reserve_saturday_dinner:
                            chosen_days_dinner.append('شنبه')
                        if pdays.reserve_sunday_dinner:
                            chosen_days_dinner.append('یکشنبه')
                        if pdays.reserve_monday_dinner:
                            chosen_days_dinner.append('دوشنبه')
                        if pdays.reserve_tuesday_dinner:
                            chosen_days_dinner.append('سه شنبه')
                        if pdays.reserve_wednesday_lunch:
                            chosen_days_dinner.append('چهارشنبه')
                        if pdays.reserve_thursday_dinner:
                            chosen_days_dinner.append('پنجشنبه')

                        total_price = 0

                        saturdays_date = list()
                        date = str(jdatetime.date.today() + jdatetime.timedelta(5))
                        date = re.sub(r'\-', '/', date)
                        saturdays_date.append(date)
                        saturdays_date = str(saturdays_date)

                        filter = ReservedTable.objects.filter(user=user_data.user, week_start_date=saturdays_date)
                        if not filter:
                            reserved = ReservedTable()
                            reserved.user = user_data.user
                            reserved.week_start_date = saturdays_date
                        else:
                            reserved = filter[0]
                        if lunch_data:
                            for item in lunch_data:
                                k = 0
                                while k < len(lunch_data[item]):
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].selected'] = \
                                        lunch_data[item][k][8]
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].id'] = ''
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].programId'] = \
                                        lunch_data[item][k][3]
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].mealTypeId'] = \
                                        lunch_data[item][k][4]
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].programDateTime'] = \
                                        lunch_data[item][k][5]
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].selfId'] = self.self_id
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].foodTypeId'] = \
                                        lunch_data[item][k][6]
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].selectedCount'] = \
                                        lunch_data[item][k][9]
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].freeFoodSelected'] = \
                                        lunch_data[item][k][7]
                                    k += 1

                        if breakfast_data:
                            for item in breakfast_data:
                                k = 0
                                while k < len(breakfast_data[item]):
                                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].selected'] = \
                                        breakfast_data[item][k][8]
                                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].id'] = ''
                                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].programId'] = \
                                        breakfast_data[item][k][3]
                                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].mealTypeId'] = \
                                        breakfast_data[item][k][4]
                                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].programDateTime'] = \
                                        breakfast_data[item][k][5]
                                    payload_reserve[
                                        f'userWeekReserves[{breakfast_data[item][k][0]}].selfId'] = self.self_id
                                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].foodTypeId'] = \
                                        breakfast_data[item][k][6]
                                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].selectedCount'] = \
                                        breakfast_data[item][k][9]
                                    payload_reserve[
                                        f'userWeekReserves[{breakfast_data[item][k][0]}].freeFoodSelected'] = \
                                        breakfast_data[item][k][7]
                                    k += 1
                        if dinner_data:
                            for item in dinner_data:
                                k = 0
                                while k < len(dinner_data[item]):
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].selected'] = \
                                        dinner_data[item][k][
                                            8]
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].id'] = ''
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].programId'] = \
                                        dinner_data[item][k][3]
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].mealTypeId'] = \
                                        dinner_data[item][k][4]
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].programDateTime'] = \
                                        dinner_data[item][k][5]
                                    payload_reserve[
                                        f'userWeekReserves[{dinner_data[item][k][0]}].selfId'] = self.self_id
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].foodTypeId'] = \
                                        dinner_data[item][k][6]
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].selectedCount'] = \
                                        dinner_data[item][k][9]
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].freeFoodSelected'] = \
                                        dinner_data[item][k][7]
                                    k += 1

                            for daye in dinner_data:
                                if dinner_data[daye]:
                                    for day in chosen_days_lunch:
                                        if daye[0] == day and (dinner_data[daye] != []):
                                            food_list = []
                                            for food in dinner_data[daye]:
                                                food_list.append((food[0],
                                                                  UserPreferableFood.objects.filter(~Q(score=0),
                                                                                                    user=user_data.user,
                                                                                                    food__name=food[1])[
                                                                      0],
                                                                  food[2]))
                                            food_list.sort(key=lambda x: x[1].score, reverse=True)
                                            prefered_data = food_list
                                            if prefered_data:
                                                payload_reserve[
                                                    f'userWeekReserves[{prefered_data[0][0]}].selected'] = 'true'
                                                payload_reserve[
                                                    f'userWeekReserves[{prefered_data[0][0]}].selectedCount'] = '1'

                                                a = int(prefered_data[0][2])
                                                total_price += a

                                                if day == 'شنبه':
                                                    reserved.saturday_dinner = prefered_data[0][1].food.name
                                                    reserved.saturday_dinner_self = self.self_name
                                                if day == 'یکشنبه':
                                                    reserved.sunday_dinner = prefered_data[0][1].food.name
                                                    reserved.sunday_dinner_self = self.self_name
                                                if day == 'دوشنبه':
                                                    reserved.monday_dinner = prefered_data[0][1].food.name
                                                    reserved.monday_dinner_self = self.self_name
                                                if day == 'سه شنبه':
                                                    reserved.tuesday_dinner = prefered_data[0][1].food.name
                                                    reserved.tuesday_dinner_self = self.self_name
                                                if day == 'چهارشنبه':
                                                    reserved.wednesday_dinner = prefered_data[0][1].food.name
                                                    reserved.wednesday_dinner_self = self.self_name
                                                if day == 'پنجشنبه':
                                                    reserved.thursday_dinner = prefered_data[0][1].food.name
                                                    reserved.thursday_dinner_self = self.self_name
                                                if day == 'جمعه':
                                                    reserved.friday_dinner = prefered_data[0][1].food.name
                                                    reserved.friday_dinner_self = self.self_name

                            for daye in lunch_data:
                                if lunch_data[daye]:
                                    for day in chosen_days_lunch:
                                        if (daye[0] == day) and (lunch_data[daye] != []):
                                            food_list = []
                                            for food in lunch_data[daye]:
                                                print(food)
                                                prefered_food = UserPreferableFood.objects.filter(~Q(score=0),
                                                                                                  user=user_data.user,
                                                                                                  food__name=food[1])
                                                print(prefered_food)
                                                food_list.append((food[0],
                                                                  prefered_food[0],
                                                                  food[2]))
                                                print(food_list)
                                            food_list.sort(key=lambda x: x[1].score, reverse=True)
                                            prefered_data = food_list
                                            if prefered_data:
                                                payload_reserve[
                                                    f'userWeekReserves[{prefered_data[0][0]}].selected'] = 'true'
                                                payload_reserve[
                                                    f'userWeekReserves[{prefered_data[0][0]}].selectedCount'] = '1'

                                                a = int(prefered_data[0][2])
                                                total_price += a

                                                if day == 'شنبه':
                                                    reserved.saturday_lunch = prefered_data[0][1].food.name
                                                    reserved.saturday_lunch_self = self.self_name
                                                if day == 'یکشنبه':
                                                    reserved.sunday_lunch = prefered_data[0][1].food.name
                                                    reserved.sunday_lunch_self = self.self_name
                                                if day == 'دوشنبه':
                                                    reserved.monday_lunch = prefered_data[0][1].food.name
                                                    reserved.monday_lunch_self = self.self_name
                                                if day == 'سه شنبه':
                                                    reserved.tuesday_lunch = prefered_data[0][1].food.name
                                                    reserved.tuesday_lunch_self = self.self_name
                                                if day == 'چهارشنبه':
                                                    reserved.wednesday_lunch = prefered_data[0][1].food.name
                                                    reserved.wednesday_lunch_self = self.self_name
                                                if day == 'پنجشنبه':
                                                    reserved.thursday_lunch = prefered_data[0][1].food.name
                                                    reserved.thursday_lunch_self = self.self_name
                                                if day == 'جمعه':
                                                    reserved.friday_lunch = prefered_data[0][1].food.name
                                                    reserved.friday_lunch_self = self.self_name

                            for daye in breakfast_data:
                                if breakfast_data[daye]:
                                    for day in chosen_days_breakfast:
                                        if daye[0] == day and (breakfast_data[daye] != []):
                                            food_list = []
                                            for food in breakfast_data[daye]:
                                                food_list.append((food[0],
                                                                  UserPreferableFood.objects.filter(~Q(score=0),
                                                                                                    user=user_data.user,
                                                                                                    food__name=food[1])[
                                                                      0],
                                                                  food[2]))
                                            print(food_list)
                                            food_list.sort(key=lambda x: x[1].score, reverse=True)
                                            print(food_list)
                                            prefered_data = food_list
                                            if prefered_data:
                                                payload_reserve[
                                                    f'userWeekReserves[{prefered_data[0][0]}].selected'] = 'true'
                                                payload_reserve[
                                                    f'userWeekReserves[{prefered_data[0][0]}].selectedCount'] = '1'
                                                print(prefered_data)
                                                a = int(prefered_data[0][2])
                                                total_price += a
                                                if day == 'شنبه':
                                                    reserved.saturday_lunch = prefered_data[0][1].food.name
                                                    reserved.saturday_breakfast_self = self.self_name
                                                if day == 'یکشنبه':
                                                    reserved.sunday_lunch = prefered_data[0][1].food.name
                                                    reserved.sunday_breakfast_self = self.self_name
                                                if day == 'دوشنبه':
                                                    reserved.monday_lunch = prefered_data[0][1].food.name
                                                    reserved.monday_breakfast_self = self.self_name
                                                if day == 'سه شنبه':
                                                    reserved.tuesday_lunch = prefered_data[0][1].food.name
                                                    reserved.tuesday_breakfast_self = self.self_name
                                                if day == 'چهارشنبه':
                                                    reserved.wednesday_lunch = prefered_data[0][1].food.name
                                                    reserved.wednesday_breakfast_self = self.self_name
                                                if day == 'پنجشنبه':
                                                    reserved.thursday_lunch = prefered_data[0][1].food.name
                                                    reserved.thursday_breakfast_self = self.self_name
                                                if day == 'جمعه':
                                                    reserved.friday_lunch = prefered_data[0][1].food.name
                                                    reserved.friday_breakfast_self = self.self_name

                                payload_reserve['remainCredit'] = Credit - total_price
                            result = session_requests.post(reserve_get_url, data=payload_reserve)
                        reserved.credit = Credit - total_price
                        reserved.save()
                        if user_data.user.chat_id != 0:
                            data = {'صبحانه': [reserved.saturday_breakfast, reserved.saturday_breakfast,
                                               reserved.monday_breakfast,
                                               reserved.tuesday_breakfast, reserved.wednesday_breakfast,
                                               reserved.tuesday_breakfast,
                                               reserved.friday_breakfast],
                                    'ناهار': [reserved.saturday_lunch, reserved.saturday_lunch, reserved.monday_lunch,
                                              reserved.tuesday_lunch, reserved.wednesday_lunch, reserved.tuesday_lunch,
                                              reserved.friday_lunch],
                                    'شام': [reserved.saturday_dinner, reserved.saturday_dinner, reserved.monday_dinner,
                                            reserved.tuesday_dinner, reserved.wednesday_dinner, reserved.tuesday_dinner,
                                            reserved.friday_dinner]}
                            df = pd.DataFrame(data,
                                              index=['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه',
                                                     'جمعه'])

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

                            try:
                                message = "سلام\nامروز چهارشنبه‌س و غذاهاتو برات رزرو کردم\nغذاهایی که رزرو کردم ایناست\n"
                                send(message, str(user_data.user.chat_id), bot_token)
                                send_photo(path='reserve_img.png', chat_id=str(user_data.user.chat_id), token=bot_token)
                            except Exception as e:
                                print(e)
                                break
                        break
                except Exception as e:
                    print(e)
                    time.sleep(5)
                    r += 1
