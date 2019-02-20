import requests
from django.shortcuts import render
from lxml import html


def charge_account_sharif(user, password, amount):
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


def charge_account_samadv1(request):
    login_url = 'https://dining.sbu.ac.ir/j_security_check'
    charge_url = 'https://dining.sbu.ac.ir/nurture/user/credit/charge/view.rose'
    charge = 'https://dining.sbu.ac.ir/nurture/user/credit/charge/charge.rose'
    session_requests = requests.session()
    result = session_requests.get(login_url, verify=False)

    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
    payload = {
        'username': '96435085',
        'password': '4480085165',
        '_csrf': authenticity_token,
        'login': 'ورود'
    }

    result = session_requests.post(login_url, data=payload, verify=False)
    result = session_requests.get(charge_url, verify=False)
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
    payload = {
        'selectedAmount': 10000,
        'customAmount': '',
        '_csrf': authenticity_token,
    }
    result = session_requests.post(charge, data=payload, verify=False)
    result = session_requests.get('https://dining.sbu.ac.ir/modules/epayment/processing/selectBank.rose?selbank=2')
    tree = html.fromstring(result.text)
    requestTransactionUrl = list(set(tree.xpath("//input[@name='requestTransactionUrl']/@value")))[0]
    Token = list(set(tree.xpath("//input[@name='Token']/@value")))[0]
    MerchantId = list(set(tree.xpath("//input[@name='MerchantId']/@value")))[0]
    payload = {
        'requestTransactionUrl': requestTransactionUrl,
        'Token': Token,
        'MerchantId': MerchantId
    }

    return render(request, 'dining/templates/charge_samad.html', payload)
