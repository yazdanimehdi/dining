import re

import requests
from bs4 import BeautifulSoup
from lxml import html

from dining.models import *

login_url = 'http://refahi.kntu.ac.ir/j_security_check'
reserve_get_url = 'http://refahi.kntu.ac.ir/nurture/user/multi/reserve/reserve.rose'
session_requests = requests.session()
result = session_requests.get(login_url, verify=False)

tree = html.fromstring(result.text)
authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
payload = {
    'username': '9621874',
    'password': '1250337968',
    '_csrf': authenticity_token,
    'login': 'ورود'
}

result = session_requests.post(login_url, data=payload, verify=False)
result = session_requests.get(reserve_get_url, verify=False)

self_id = re.findall(r'<option value=\"(.+?)\"', result.text)
self_names = re.findall(r'<option value=\".*\">(.+)</option>', result.text)
self_ids = set(self_id)
for self in self_id:
    result = session_requests.get(
        f'http://refahi.kntu.ac.ir/nurture/user/multi/reserve/showPanel.rose?selectedSelfDefId={self}', verify=False)
    w = 0
    while w < 54:
        tree = html.fromstring(result.text)
        authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
        weekStartDateTime = list(set(tree.xpath("//input[@name='weekStartDateTime']/@value")))[0]
        weekStartDateTimeAjx = list(set(tree.xpath("//input[@name='weekStartDateTimeAjx']/@value")))[0]
        remainCredit = list(set(tree.xpath("//input[@name='remainCredit']/@value")))[0]
        payload_reserve = {
            'method:showPreviousWeek': 'Submit',
            'weekStartDateTime': weekStartDateTime,
            'remainCredit': remainCredit,
            'selfChangeReserveId': '',
            'weekStartDateTimeAjx': weekStartDateTimeAjx,
            'selectedSelfDefId': self,
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
            weekStartDateTime = list(set(tree.xpath("//*[@id=\"resFinalform_weekStartDateTime\"]/@value")))[
                0]
            weekStartDateTimeAjx = list(set(tree.xpath("//input[@name='weekStartDateTimeAjx']/@value")))[0]
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
                        payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].selected'] = lunch_data[item][k][8]
                        payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].id'] = ''
                        payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].programId'] = \
                            lunch_data[item][k][3]
                        payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].mealTypeId'] = \
                            lunch_data[item][k][4]
                        payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].programDateTime'] = \
                            lunch_data[item][k][5]
                        payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].selfId'] = self
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
                        payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].selfId'] = self
                        payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].foodTypeId'] = \
                            breakfast_data[item][k][6]
                        payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].selectedCount'] = \
                        breakfast_data[item][k][9]
                        payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].freeFoodSelected'] = \
                            breakfast_data[item][k][7]
                        k += 1
            if dinner_data:
                for item in dinner_data:
                    k = 0
                    while k < len(dinner_data[item]):
                        payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].selected'] = dinner_data[item][k][
                            8]
                        payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].id'] = ''
                        payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].programId'] = \
                            dinner_data[item][k][3]
                        payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].mealTypeId'] = \
                            dinner_data[item][k][4]
                        payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].programDateTime'] = \
                            dinner_data[item][k][5]
                        payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].selfId'] = self
                        payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].foodTypeId'] = \
                            dinner_data[item][k][6]
                        payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].selectedCount'] = \
                        dinner_data[item][k][9]
                        payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].freeFoodSelected'] = \
                            dinner_data[item][k][7]
                        k += 1
        result = session_requests.post('http://refahi.kntu.ac.ir/nurture/user/multi/reserve/reserve.rose',
                                       data=payload_reserve, verify=False)
        m = 0
        food_name = list()
        while tree.xpath(f"//*[@id=\"foodNameSpan{m}\"]/text()"):
            food_name.append(str(tree.xpath(f"//*[@id=\"foodNameSpan{m}\"]/text()")[0]))
            m += 1
        for item in food_name:
            flag = False
            item = re.findall(r'\|(.+)', item)[0].split('|')[0].strip()
            print(item)
            if Food.objects.filter(university__name='دانشگاه صنعتی خواجه نصیر الدین طوسی'):
                for db_food in Food.objects.filter(university__name='دانشگاه صنعتی خواجه نصیر الدین طوسی'):
                    if set(db_food.name.split(' ')).issubset(item.split(' ')):
                        flag = True
                    elif db_food.name in item:
                        flag = True

                if not flag:
                    uni = University.objects.get(name='دانشگاه صنعتی خواجه نصیر الدین طوسی')
                    newfood = Food()
                    newfood.name = item.strip()
                    newfood.university = uni
                    newfood.save()
            else:
                uni = University.objects.get(name='دانشگاه صنعتی خواجه نصیر الدین طوسی')
                newfood = Food()
                newfood.name = item.strip()
                newfood.university = uni
                newfood.save()
        w += 1
