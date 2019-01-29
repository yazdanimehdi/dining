import jdatetime
from django.shortcuts import render, redirect

from dining.models import CustomUser, Coins, ZorroCode


def payment(request):
    if request.user.is_authenticated:
        u = CustomUser.objects.get(username=request.user)
        coin = Coins.objects.filter(user=request.user, active=True)
        a = coin.count()
        coinss = list(coin)
        date_time = str(jdatetime.datetime.now()).split(' ')
        date = date_time[0]
        time = date_time[1]

        if request.method == 'GET':
            if u.is_paid:
                return render(request, 'dining/templates/dashboard.html',
                              {'msg': '!اکانتت فعاله لذت ببر',
                               'color': '#39b54a', 'coin': a, 'username': u.username})
            else:
                return render(request, 'dining/templates/peyment.html', {'date': date, 'time': time, 'coin': a, })
        elif request.method == 'POST':
            if request.POST.get('choice') == 'online_payment':
                request.session['amount'] = 10000
                request.session['code'] = '-'
                return redirect('/payment/request/')
            elif request.POST.get('choice') == 'coin':
                if a >= 4:
                    i = 0
                    while i < 4:
                        coinss[i].active = False
                        coinss[i].save()
                        i += 1
                    coin = Coins.objects.filter(user=request.user, active=True).count()
                    u.is_paid = True
                    u.save()
                    return render(request, 'dining/templates/dashboard.html', {
                        'msg': '!پرداخت با موفقیت انجام شد از این به بعد مسترزرو خودش برات غذا رزرو می‌کنه\n'
                               'عضو شدن توی ربات یادت نره!',
                        'color': '#39b54a', 'coin': coin, 'username': u.username})
                else:
                    return render(request, 'dining/templates/peyment.html',
                                  {'date': date, 'time': time, 'coin': a, 'msg': '!به اندازه‌ی کافی سکه نداری'})
            elif request.POST.get('choice') == 'zorocode':
                zorocode = request.POST.get('zorocode')
                code_objects = list(ZorroCode.objects.filter(code=zorocode))
                if not code_objects:
                    return render(request, 'dining/templates/peyment.html',
                                  {'date': date, 'time': time, 'coin': a, 'msg': '!زروکدت معتبر نیست'})
                else:
                    if not code_objects[0].active:
                        return render(request, 'dining/templates/peyment.html',
                                      {'date': date, 'time': time, 'coin': a, 'msg': '!زروکدت قبلا استفاده شده'})
                    else:
                        code_objects[0].time_used = code_objects[0].time_used + 1
                        code_objects[0].save()
                        if code_objects[0].time_used >= code_objects[0].max_time:
                            code_objects[0].active = False
                            code_objects[0].save()
                        if code_objects[0].percent == 100:
                            u.is_paid = True
                            u.code_used = code_objects[0].code
                            u.save()
                            return render(request, 'dining/templates/dashboard.html', {
                                'msg': '!پرداخت با موفقیت انجام شد از این به بعد مسترزرو خودش برات غذا رزرو می‌کنه',
                                'color': '#39b54a', 'coin': a, 'username': u.username})
                        if code_objects[0].percent < 100:
                            request.session['amount'] = 100 * (100 - code_objects[0].percent)
                            request.session['code'] = code_objects[0].code
                            return redirect('/payment/request/')

    else:
        return redirect('/login')
