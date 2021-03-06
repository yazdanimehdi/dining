import os
import re
import sys

import imgkit
import jdatetime
import pandas as pd
import requests
import telegram
from bs4 import BeautifulSoup
from celery import task
from lxml import html


@task()
def samadv1_get_reserved_function():
    from dining.models import UserDiningData, ReservedTable, UserSelfs

    for user_data in UserDiningData.objects.filter(university__tag='samadv1'):
        login_url = user_data.university.login_url
        reserve_get_url = user_data.university.reserve_url
        simple = user_data.university.simple_url
        if user_data.user.is_paid:
            try:
                saturdays_date = list()
                date = str(jdatetime.date.today() + jdatetime.timedelta(3))
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

                for self in UserSelfs.objects.filter(user=user_data.user, is_active=True):
                    session_requests = requests.session()
                    result = session_requests.get(login_url, verify=False)
                    tree = html.fromstring(result.text)
                    authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
                    payload = {
                        'username': user_data.dining_username,
                        'password': user_data.dining_password,
                        '_csrf': authenticity_token,
                        'login': 'ورود'
                    }

                    result = session_requests.post(login_url, data=payload, verify=False)
                    result = session_requests.get(reserve_get_url, verify=False)
                    tree = html.fromstring(result.text)
                    result = session_requests.get(
                        f'{simple}/nurture/user/multi/reserve/showPanel.rose?selectedSelfDefId={self.self_id}',
                        verify=False)
                    tree = html.fromstring(result.text)
                    authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
                    weekStartDateTime = list(set(tree.xpath("//input[@name='weekStartDateTime']/@value")))[0]
                    weekStartDateTimeAjx = list(set(tree.xpath("//input[@name='weekStartDateTimeAjx']/@value")))[0]
                    remainCredit = list(set(tree.xpath("//input[@name='remainCredit']/@value")))[0]
                    payload_reserve = {
                        'method:showNextWeek': 'Submit',
                        'weekStartDateTime': weekStartDateTime,
                        'remainCredit': remainCredit,
                        'selfChangeReserveId': '',
                        'weekStartDateTimeAjx': weekStartDateTimeAjx,
                        'selectedSelfDefId': self.self_id,
                        '_csrf': authenticity_token,
                    }
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
                            food_name = re.findall(r'this.offsetLeft, this.offsetTop\);\">\s+(.+)', str(soupf))[0]
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
                                    payload_reserve[
                                        f'userWeekReserves[{lunch_data[item][k][0]}].selfId'] = self.self_id
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].foodTypeId'] = \
                                        lunch_data[item][k][6]
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].selectedCount'] = \
                                        lunch_data[item][k][9]
                                    payload_reserve[
                                        f'userWeekReserves[{lunch_data[item][k][0]}].freeFoodSelected'] = \
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
                                    payload_reserve[
                                        f'userWeekReserves[{breakfast_data[item][k][0]}].programDateTime'] = \
                                        breakfast_data[item][k][5]
                                    payload_reserve[
                                        f'userWeekReserves[{breakfast_data[item][k][0]}].selfId'] = self.self_id
                                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].foodTypeId'] = \
                                        breakfast_data[item][k][6]
                                    payload_reserve[
                                        f'userWeekReserves[{breakfast_data[item][k][0]}].selectedCount'] = \
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
                                    payload_reserve[
                                        f'userWeekReserves[{dinner_data[item][k][0]}].programDateTime'] = \
                                        dinner_data[item][k][5]
                                    payload_reserve[
                                        f'userWeekReserves[{dinner_data[item][k][0]}].selfId'] = self.self_id
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].foodTypeId'] = \
                                        dinner_data[item][k][6]
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].selectedCount'] = \
                                        dinner_data[item][k][9]
                                    payload_reserve[
                                        f'userWeekReserves[{dinner_data[item][k][0]}].freeFoodSelected'] = \
                                        dinner_data[item][k][7]
                                    k += 1
                    result = session_requests.post(
                        reserve_get_url,
                        data=payload_reserve, verify=False)

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
                            mealTypeId = re.findall(r'mealTypeId\" type=\"hidden\" value=\"(.+)\"', str(soupf))[
                                0]
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
                                selected = \
                                    tree.xpath(f"//*[@id=\"userWeekReserves.selected{j}_hidden\"]/@value")[0]
                            else:
                                if 'null' in tree.xpath(f'//*[@id=\"userWeekReserves.selected{j}\"]/@onclick')[
                                    0]:
                                    selected = 'false'
                                else:
                                    selected = 'true'
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

                    for day, date in lunch_data:
                        for item in lunch_data[(day, date)]:
                            if item[8] == 'true':
                                if day == 'شنبه':
                                    reserved.saturday_lunch = item[1]
                                    reserved.saturday_lunch_self = self.self_name
                                if day == 'یکشنبه':
                                    reserved.sunday_lunch = item[1]
                                    reserved.sunday_lunch_self = self.self_name
                                if day == 'دوشنبه':
                                    reserved.monday_lunch = item[1]
                                    reserved.monday_lunch_self = self.self_name
                                if day == 'سه شنبه':
                                    reserved.tuesday_lunch = item[1]
                                    reserved.tuesday_lunch_self = self.self_name
                                if day == 'چهارشنبه':
                                    reserved.wednesday_lunch = item[1]
                                    reserved.wednesday_lunch_self = self.self_name
                                if day == 'پنجشنبه':
                                    reserved.thursday_lunch = item[1]
                                    reserved.thursday_lunch_self = self.self_name
                                if day == 'جمعه':
                                    reserved.friday_lunch = item[1]
                                    reserved.friday_lunch_self = self.self_name

                    for day, date in dinner_data:
                        for item in dinner_data[(day, date)]:
                            if item[8] == 'true':
                                if day == 'شنبه':
                                    reserved.saturday_dinner = item[1]
                                    reserved.saturday_dinner_self = self.self_name
                                if day == 'یکشنبه':
                                    reserved.sunday_dinner = item[1]
                                    reserved.sunday_dinner_self = self.self_name
                                if day == 'دوشنبه':
                                    reserved.monday_dinner = item[1]
                                    reserved.monday_dinner_self = self.self_name
                                if day == 'سه شنبه':
                                    reserved.tuesday_dinner = item[1]
                                    reserved.tuesday_dinner_self = self.self_name
                                if day == 'چهارشنبه':
                                    reserved.wednesday_dinner = item[1]
                                    reserved.wednesday_dinner_self = self.self_name
                                if day == 'پنجشنبه':
                                    reserved.thursday_dinner = item[1]
                                    reserved.thursday_dinner_self = self.self_name
                                if day == 'جمعه':
                                    reserved.friday_dinner = item[1]
                                    reserved.friday_dinner_self = self.self_name

                    for day, date in breakfast_data:
                        for item in breakfast_data[(day, date)]:
                            if item[8] == 'true':
                                if day == 'شنبه':
                                    reserved.saturday_breakfast = item[1]
                                    reserved.saturday_breakfast_self = self.self_name
                                if day == 'یکشنبه':
                                    reserved.sunday_breakfast = item[1]
                                    reserved.sunday_breakfast_self = self.self_name
                                if day == 'دوشنبه':
                                    reserved.monday_breakfast = item[1]
                                    reserved.monday_breakfast_self = self.self_name
                                if day == 'سه شنبه':
                                    reserved.tuesday_breakfast = item[1]
                                    reserved.tuesday_breakfast_self = self.self_name
                                if day == 'چهارشنبه':
                                    reserved.wednesday_breakfast = item[1]
                                    reserved.wednesday_breakfast_self = self.self_name
                                if day == 'پنجشنبه':
                                    reserved.thursday_breakfast = item[1]
                                    reserved.thursday_breakfast_self = self.self_name
                                if day == 'جمعه':
                                    reserved.friday_breakfast = item[1]
                                    reserved.friday_breakfast_self = self.self_name
                    reserved.credit = Credit
                    reserved.save()
                if user_data.user.chat_id != 0:
                    bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'

                    def send_photo(path, chat_id, token):
                        bot = telegram.Bot(token=token)
                        bot.send_photo(chat_id=chat_id, photo=open(path, 'rb'))

                    def send(msg, chat_id, token):
                        bot = telegram.Bot(token=token)
                        bot.send_message(chat_id=chat_id, text=msg)

                    data = {'صبحانه': [reserved.saturday_breakfast, reserved.sunday_breakfast,
                                       reserved.monday_breakfast,
                                       reserved.tuesday_breakfast, reserved.wednesday_breakfast,
                                       reserved.thursday_breakfast,
                                       reserved.friday_breakfast],
                            'ناهار': [reserved.saturday_lunch, reserved.sunday_lunch, reserved.monday_lunch,
                                      reserved.tuesday_lunch, reserved.wednesday_lunch, reserved.thursday_lunch,
                                      reserved.friday_lunch],
                            'شام': [reserved.saturday_dinner, reserved.sunday_dinner, reserved.monday_dinner,
                                    reserved.tuesday_dinner, reserved.wednesday_dinner,
                                    reserved.thursday_dinner,
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
                                               text-align: center;
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
                    message = 'غذاهایی که برات رزرو شده ایناهاست'
                    try:
                        send(message, str(user_data.user.chat_id), bot_token)
                        send_photo(path='reserve_img.png', chat_id=str(user_data.user.chat_id), token=bot_token)
                    except Exception as e:
                        print(e)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
