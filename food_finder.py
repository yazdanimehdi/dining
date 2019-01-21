import re

import requests
from bs4 import BeautifulSoup
from lxml import html

from dining.models import University, Food

login_url = 'http://stu.iust.ac.ir/j_security_check'
reserve_get_url = 'http://stu.iust.ac.ir/nurture/user/multi/reserve/reserve.rose'
session_requests = requests.session()
result = session_requests.get(login_url)

tree = html.fromstring(result.text)
authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
payload = {
    'username': '96671181',
    'password': '0017579783',
    '_csrf': authenticity_token,
}

result = session_requests.post(login_url, data=payload, headers=dict(referer=login_url))
result = session_requests.get(reserve_get_url)

self_id = re.findall(r'<option value=\"(.+?)\"', result.text)
self_names = re.findall(r'<option value=\".*\">(.+)</option>', result.text)
self_ids = set(self_id)

tree = html.fromstring(result.text)

authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
weekStartDateTime = list(set(tree.xpath("//input[@name='weekStartDateTime']/@value")))[0]
weekStartDateTimeAjx = list(set(tree.xpath("//input[@name='weekStartDateTimeAjx']/@value")))[0]

remainCredit = list(set(tree.xpath("//input[@name='remainCredit']/@value")))[0]

for ids in self_ids:
    k = 0
    while k < 54:
        food_list = list()
        payload_load = {
            # 'method:showNextWeek': 'Submit',
            'method:showCurrentWeek': 'Submit',
            'weekStartDateTime': weekStartDateTime,
            'remainCredit': remainCredit,
            'selfChangeReserveId': '',
            'weekStartDateTimeAjx': weekStartDateTimeAjx,
            'selectedSelfDefId': ids,
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
                str(soup_find[i]))[0]
            date = re.findall(r'<div>(.+)</div>', str(soup_find[i]))[0]
            weekStartDateTime = list(set(tree.xpath("//*[@id=\"resFinalform_weekStartDateTime\"]/@value")))[0]
            weekStartDateTimeAjx = list(set(tree.xpath("//input[@name='weekStartDateTimeAjx']/@value")))[0]
            foods_lunch = list()
            foods_dinner = list()
            foods_breakfast = list()
            for soupf in soup_find[i].find_all('tr'):
                food_name = re.findall(r'this.offsetLeft, this.offsetTop\);\">\s+(.+)', str(soupf))
            flag = False
            for db_food in Food.objects.filter(university__name='University Of Science And Technology'):
                if set(db_food.food.name.split(' ')).issubset(food_name.split(' ')):
                    pass
                elif db_food.food.name in food_name:
                    pass
                else:
                    uni = University.objects.get(name='University Of Science And Technology')
                    newfood = Food()
                    newfood.name = re.findall(r'\|(.+)', food_name)[0]
                    newfood.university = uni
                    newfood.save()
            i += 1
        k += 1
