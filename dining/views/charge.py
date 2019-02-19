import requests
from lxml import html


def charge_account(user, password, amount):
    # login in
    login_url = 'http://dining.sharif.ir/login'
    url_payment = 'http://dining.sharif.ir/admin/payment/payment/charge'
    url_reserved_table = 'http://dining.sharif.ir/admin/food/food-reserve/load-reserved-table'
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
    result = session_requests.get(url_payment)
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
    payload_charge = {
        '_csrf': authenticity_token,
        'PaymentsForm[amount]': amount,
        'paysharif': ''

    }
    result = session_requests.post(url_payment, data=payload_charge)
    return result.url
