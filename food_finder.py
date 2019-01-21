import re

import requests
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

for ids in ['11']:
    k = 0
    while k < 200:
        tree = html.fromstring(result.text)
        authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
        weekStartDateTime = list(set(tree.xpath("//input[@name='weekStartDateTime']/@value")))[0]
        weekStartDateTimeAjx = list(set(tree.xpath("//input[@name='weekStartDateTimeAjx']/@value")))[0]

        remainCredit = list(set(tree.xpath("//input[@name='remainCredit']/@value")))[0]
        food_list = list()
        payload_load = {
            'method:showPreviousWeek': 'Submit',
            'weekStartDateTime': weekStartDateTime,
            'remainCredit': remainCredit,
            'selfChangeReserveId': '',

            'weekStartDateTimeAjx': weekStartDateTimeAjx,
            'selectedSelfDefId': ids,
            '_csrf': authenticity_token,
        }
        result = session_requests.post(reserve_get_url, data=payload_load)
        food_name = re.findall(r'xstooltip_hide\(\'foodPriceTooltip.+\s+(.+)', result.text)
        flag = False
        for item in food_name:
            item = re.findall(r'\|(.+)', item)[0].split('|')[0]
            if Food.objects.filter(university__name='University Of Science And Technology'):
                for db_food in Food.objects.filter(university__name='دانشگاه علم و صنعت'):
                    if set(db_food.name.split(' ')).issubset(item.split(' ')):
                        flag = True
                    elif db_food.name in item:
                        flag = True
                    elif '+' in item:
                        if db_food.name in item.split('+')[0]:
                            flag = True
                        elif db_food.name in item.split('+')[1]:
                            flag = True

                if not flag:
                    uni = University.objects.get(name='University Of Science And Technology')
                    newfood = Food()
                    newfood.name = item
                    newfood.university = uni
                    newfood.save()
            else:
                uni = University.objects.get(name='دانشگاه علم و صنعت')
                newfood = Food()
                newfood.name = item
                newfood.university = uni
                newfood.save()
        k += 1
