import random
import string

from django.http import HttpResponse
from django.shortcuts import redirect
from zeep import Client
from zeep.transports import Transport

from order.models import InvoicePendingPayment

MERCHANT = 'ac663104-083d-11e9-82ac-005056a205be'
email = 'info@mrzoro.ir'  # Optional
mobile = '09124156965'  # Optional
CallbackURL = 'http://www.mrzoro.ir/payment/verify_order?code='  # Important: need to edit for realy server.
transport = Transport(timeout=20)
payment_channel_url = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'

client = None


def initialize_client():
    global client
    client = Client(payment_channel_url, transport=transport)


def generate_payment_link(user, invoice, discount_code):
    pending_payment = InvoicePendingPayment()
    pending_payment.invoice = invoice
    pending_payment.user = user
    pending_payment.amount = invoice.amount
    pending_payment.code = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
    pending_payment.discount_code = discount_code
    description = f"{invoice.amount} تومن بابت سفارش غذا "

    if client is None:
        try:
            initialize_client()
        except Exception as e:
            print(e)
            return None, '<html><body><h1>درگاه پرداخت با مشکل مواجه شده است. لطفا بعدا تلاش کنید.</h1></body></html>'

    result = client.service.PaymentRequest(MERCHANT, pending_payment.amount, description, email, mobile,
                                           CallbackURL + pending_payment.code)
    if result.Status == 100:
        pending_payment.save()
        return 'https://www.zarinpal.com/pg/StartPay/' + str(result.Authority), None
    else:
        return None, 'Error code: ' + str(result.Status)


def send_request(request):
    link, error = generate_payment_link(request.user, request.session['amount'], request.session['code'])
    if not error:
        redirect(link)
    else:
        return HttpResponse(error)


def verify_order(request):
    if request.GET.get('Status') == 'OK' and 'code' in request.GET:
        try:
            pending_payment = InvoicePendingPayment.objects.get(code=request.GET.get('code'))
        except:
            return HttpResponse('پرداخت موفقیت آمیز نبوده')

        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], pending_payment.amount)
        if result.Status == 100:
            pending_payment.is_active = True
            pending_payment.save()
            pending_payment.invoice.is_paid = True
            pending_payment.invoice.is_active = True
            pending_payment.invoice.save()

            return HttpResponse('پرداختت موفقیت آمیز بود برو داخل روبات و گزینه‌ي پرداخت کردم رو لمس کن')
        elif result.Status == 101:
            return HttpResponse(
                'Transaction submitted : ' + str(result.Status) + '<a href="/dashboard/">بازگشت به داشبورد</a>')
        else:
            return HttpResponse(
                'Transaction failed.\nStatus: ' + str(
                    result.Status) + '<a href="/dashboard/">بازگشت به داشبورد</a>')
    else:
        return redirect(to='/dashboard/')
