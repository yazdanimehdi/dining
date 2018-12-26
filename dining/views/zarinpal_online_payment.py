from django.http import HttpResponse
from django.shortcuts import redirect, render
from zeep import Client

from dining.models import CustomUser, Coins

MERCHANT = 'ac663104-083d-11e9-82ac-005056a205be'
client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
amount = 10000  # Toman / Required
description = "10000 تومن بابت خدمت رزرواسیون آنلاین مسترزرو"  # Required
email = 'info@mrzoro.ir'  # Optional
mobile = '09124156965'  # Optional
CallbackURL = 'http://www.mrzoro.ir/payment/verify/'  # Important: need to edit for realy server.


def send_request(request):
    result = client.service.PaymentRequest(MERCHANT, amount, description, email, mobile, CallbackURL)
    if result.Status == 100:
        return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
    else:
        return HttpResponse('Error code: ' + str(result.Status))


def verify(request):
    if request.GET.get('Status') == 'OK':
        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], amount)
        if result.Status == 100:
            coin = Coins.objects.get(introduced_user=request.user)
            coin.active = True
            u = CustomUser.objects.get(username=request.user)
            u.is_paid = True
            coin = Coins.objects.filter(user=request.user, active=True).count()
            return render(request, 'dining/templates/dashboard.html', {
                'msg': '!پرداخت با موفقیت انجام شد از این به بعد مسترزرو خودش برات غذا رزرو می‌کنه',
                'color': '#39b54a', 'coin': coin, 'ref_id': str(result.RefID)})
        elif result.Status == 101:
            return HttpResponse(
                'Transaction submitted : ' + str(result.Status) + '<a href="/dashboard/">بازگشت به داشبورد</a>')
        else:
            return HttpResponse(
                'Transaction failed.\nStatus: ' + str(result.Status) + '<a href="/dashboard/">بازگشت به داشبورد</a>')
    else:
        return redirect(to='/dashboard/')
