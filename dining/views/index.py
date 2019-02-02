from django.core.mail import send_mail
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render

from dining.models import University, UserDiningData


def home(request):
    uni = University.objects.count()
    count = UserDiningData.objects.filter(reserve_friday_breakfast=True).count() + UserDiningData.objects.filter(
        reserve_saturday_breakfast=True).count() + UserDiningData.objects.filter(
        reserve_sunday_breakfast=True).count() + \
            UserDiningData.objects.filter(reserve_monday_breakfast=True).count() + UserDiningData.objects.filter(
        reserve_tuesday_breakfast=True).count() + UserDiningData.objects.filter(
        reserve_wednesday_breakfast=True).count() + \
            UserDiningData.objects.filter(reserve_thursday_breakfast=True).count() + UserDiningData.objects.filter(
        reserve_friday_lunch=True).count() + UserDiningData.objects.filter(
        reserve_saturday_lunch=True).count() + UserDiningData.objects.filter(reserve_sunday_lunch=True).count() + \
            UserDiningData.objects.filter(reserve_monday_lunch=True).count() + UserDiningData.objects.filter(
        reserve_tuesday_lunch=True).count() + UserDiningData.objects.filter(reserve_wednesday_lunch=True).count() + \
            UserDiningData.objects.filter(reserve_thursday_lunch=True).count() + UserDiningData.objects.filter(
        reserve_friday_dinner=True).count() + UserDiningData.objects.filter(
        reserve_saturday_dinner=True).count() + UserDiningData.objects.filter(reserve_sunday_dinner=True).count() + \
            UserDiningData.objects.filter(reserve_monday_dinner=True).count() + UserDiningData.objects.filter(
        reserve_tuesday_dinner=True).count() + UserDiningData.objects.filter(reserve_wednesday_dinner=True).count() + \
            UserDiningData.objects.filter(reserve_thursday_dinner=True).count()

    saved = count * 10000 / (3)
    if request.method == "GET":
        return render(request, "dining/templates/index.html", {'uni': uni, 'r_count': count, 'saved': saved})
    else:
        return HttpResponseForbidden()


def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('contactName')
        subject = request.POST.get('contactSubject')
        message = request.POST.get('contactMessage')
        from_email = request.POST.get('contactEmail')
        if subject and message and from_email:
            try:
                send_mail(subject + ' : ' + from_email, f'from : {name}' + '\n' + message, 'contact@mrzoro.ir',
                          ['khodabandeh.ali7@gmail.com'])
            except:
                return HttpResponse(status=400, content='{"msg":  "یه چیزی اشتباه پیش رفت"}')
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400, content='{"msg": "تمامی فیلدها را پر کنید"}')
    else:
        return HttpResponseForbidden()
