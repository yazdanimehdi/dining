import re

import requests
from lxml import html

from dining.models import UserDiningData


def cancel_reserve(id_cancel, user):
    user_data = UserDiningData.objects.get(user=user)
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
    cookies = session_requests.cookies
    result = session_requests.get(user_data.university.reserve_table)
    regex_find = re.findall(r'load_diet_reserve_table\((.*)\);\">هفته بعد', result.text)
    if regex_find:
        user_id = re.findall(r'\,(\d\d+)', regex_find[0])[0]
    else:
        raise ValueError
    session_requests.post('http://dining.sharif.ir/admin/food/food-reserve/cancel-reserve?user_id=' + user_id,
                          data={'id': id_cancel})

    return cookies, user_id


def modify_reserve(user, id_cancel, id_reserve, self_id):
    session_requests = requests.session()
    cookies, user_id = cancel_reserve(id_cancel, user)
    session_requests.cookies = cookies
    food_reserve_request = {
        'id': id_reserve,
        'place_id': self_id,
        'food_place_id': '0',
        'self_id': self_id,
        'user_id': user_id
    }
    session_requests.post('http://dining.sharif.ir/admin/food/food-reserve/do-reserve-from-diet?user_id=' + user_id,
                          data=food_reserve_request)


def do_reserve(user, id_reserve, self_id):
    user_data = UserDiningData.objects.get(user=user)
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
        raise ValueError
    food_reserve_request = {
        'id': id_reserve,
        'place_id': self_id,
        'food_place_id': '0',
        'self_id': self_id,
        'user_id': user_id
    }
    result = session_requests.post(
        'http://dining.sharif.ir/admin/food/food-reserve/do-reserve-from-diet?user_id=' + user_id,
        data=food_reserve_request)
    if result.json()['success'] is True:
        return True
