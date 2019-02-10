import random
import string

from django.http import HttpResponse
from django.shortcuts import redirect, render
from zeep import Client
from zeep.transports import Transport

from dining.models import Coins, PendingPayment

MERCHANT = 'ac663104-083d-11e9-82ac-005056a205be'
email = 'info@mrzoro.ir'  # Optional
mobile = '09124156965'  # Optional
CallbackURL = 'http://www.mrzoro.ir/payment/verify?code='  # Important: need to edit for realy server.
transport = Transport(timeout=20)
payment_channel_url = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'

client = None


def initialize_client():
    global client
    client = Client(payment_channel_url, transport=transport)


def generate_payment_link(user, amount, discount_code):
    pending_payment = PendingPayment()
    pending_payment.user = user
    pending_payment.code = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
    pending_payment.amount = amount
    pending_payment.discount_code = discount_code
    description = f"{pending_payment.amount} تومن بابت خدمت رزرواسیون آنلاین مسترزرو"

    if client is None:
        try:
            initialize_client()
        except Exception as e:
            print(e)
            return None, '<html><body><h1>درگاه پرداخت با مشکل مواجه شده است. لطفا بعدا تلاش کنید.</h1></body></html>'

    # with client.options(timeout=5):
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


def verify(request):
    if request.GET.get('Status') == 'OK' and 'code' in request.GET:
        try:
            pending_payment = PendingPayment.objects.get(code=request.GET.get('code'))
        except PendingPayment.DoesNotExist:
            return HttpResponse('Transaction failed. <a href="/dashboard/">بازگشت به داشبورد</a>')

        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], pending_payment.amount)
        if result.Status == 100:
            try:
                coin = Coins.objects.get(introduced_user=pending_payment.user)
                coin.active = True
            except:
                pass
            user = pending_payment.user
            user.is_paid = True
            user.code_used = pending_payment.discount_code
            user.save()
            coin = Coins.objects.filter(user=user, active=True).count()
            pending_payment.delete()
            return render(request, 'dining/templates/dashboard.html', {
                'msg': '!پرداخت با موفقیت انجام شد از این به بعد مسترزرو خودش برات غذا رزرو می‌کنه',
                'color': '#39b54a', 'coin': coin, 'username': user.username, 'ref_id': str(result.RefID)})
        elif result.Status == 101:
            return HttpResponse(
                'Transaction submitted : ' + str(result.Status) + '<a href="/dashboard/">بازگشت به داشبورد</a>')
        else:
            return HttpResponse(
                'Transaction failed.\nStatus: ' + str(
                    result.Status) + '<a href="/dashboard/">بازگشت به داشبورد</a>')
    else:
        return redirect(to='/dashboard/')
