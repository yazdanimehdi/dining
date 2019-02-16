import re

import requests
from lxml import html


def forget(user, password, self, meal):
    login_url = 'http://dining.sharif.ir/login'
    url_forget = 'http://dining.sharif.ir/admin/food/forgotten-code/get-food-diets'
    get_forgotten = 'http://dining.sharif.ir/admin/food/forgotten-code/get-forgotten-code'
    session_requests = requests.session()
    result = session_requests.get(login_url)

    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
    payload = {
        'LoginForm[username]': user,
        'LoginForm[password]': password,
        '_csrf': authenticity_token
    }
    result = session_requests.post(login_url, data=payload, headers=dict(referer=login_url))
    payload = {
        'self_id': self,
        'food_place_id': '0',
        'food_meal_id': meal
    }

    result = session_requests.post(url_forget, data=payload)
    id_food = re.findall(r'get_forgotten_code\((\d+),', result.text)

    if id_food:
        payload = {
            'id': id_food[0]
        }
        result = session_requests.post(get_forgotten, data=payload)
        return result.json()['code']

    else:
        return 'کد فراموشیی موجود نمی‌باشد'
