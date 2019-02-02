from django.http import HttpResponse
from django.shortcuts import redirect, render
from zeep import Client
from zeep.transports import Transport

from dining.models import CustomUser, Coins

MERCHANT = 'ac663104-083d-11e9-82ac-005056a205be'
email = 'info@mrzoro.ir'  # Optional
mobile = '09124156965'  # Optional
CallbackURL = 'http://www.mrzoro.ir/payment/verify/'  # Important: need to edit for realy server.
transport = Transport(timeout=5)
payment_channel_url = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'

client = None


def initialize_client():
    global client
    client = Client(payment_channel_url, transport=transport)


def send_request(request):
    request.session['user'] = request.user.username
    amount = request.session['amount']
    description = "%s تومن بابت خدمت رزرواسیون آنلاین مسترزرو" % amount
    if client is None:
        try:
            initialize_client()
        except Exception:
            return HttpResponse(
                content='<html><body><h1>درگاه پرداخت با مشکل مواجه شده است. لطفا بعدا تلاش کنید.</h1></body></html>')
    # with client.options(timeout=5):
    result = client.service.PaymentRequest(MERCHANT, amount, description, email, mobile,
                                           CallbackURL)
    if result.Status == 100:
        return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
    else:
        return HttpResponse('Error code: ' + str(result.Status))


def verify(request):
    if request.GET.get('Status') == 'OK':
        # with client.options(timeout=5):
        amount = request.session['amount']
        username = request.session['user']
        code = request.session['code']
        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], amount)
        if result.Status == 100:
            try:
                coin = Coins.objects.get(introduced_user__username=username)
                coin.active = True
            except:
                pass
            u = CustomUser.objects.get(username=username)
            u.is_paid = True
            u.code_used = code
            u.save()
            coin = Coins.objects.filter(user__username=username, active=True).count()
            del request.session['user']
            del request.session['code']
            del request.session['amount']

            return render(request, 'dining/templates/dashboard.html', {
                'msg': '!پرداخت با موفقیت انجام شد از این به بعد مسترزرو خودش برات غذا رزرو می‌کنه',
                'color': '#39b54a', 'coin': coin, 'username': u.username, 'ref_id': str(result.RefID)})
        elif result.Status == 101:
            return HttpResponse(
                'Transaction submitted : ' + str(result.Status) + '<a href="/dashboard/">بازگشت به داشبورد</a>')
        else:
            return HttpResponse(
                'Transaction failed.\nStatus: ' + str(
                    result.Status) + '<a href="/dashboard/">بازگشت به داشبورد</a>')
    else:
        return redirect(to='/dashboard/')
