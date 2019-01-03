from django.shortcuts import render, redirect

from dining.models import UserDiningData, Coins


def change_info_dining(request):
    if request.user.is_authenticated:
        c = UserDiningData.objects.filter(user=request.user)
        a = Coins.objects.filter(user=request.user, active=True).count()
        if request.method == 'GET':
            if c:
                u = UserDiningData.objects.get(user=request.user)
                return render(request, 'dining/templates/change_info_dining.html',
                              {'username': u.dining_username,
                               'password': u.dining_password})
            else:
                return redirect('/wizard')
        elif request.method == 'POST':
            u = UserDiningData.objects.get(user=request.user)
            try:
                u.dining_username = request.POST.get('dining_username')
                u.dining_password = request.POST.get('dining_password')
                u.save()
            except:
                return render(request, 'dining/templates/change_info_dining.html',
                              {'username': u.dining_username,
                               'password': u.dining_password,
                               'msg': 'یه مشکلی پیش اومده دوباره تلاش کن'})

            return render(request, 'dining/templates/dashboard.html',
                          {'msg': ' !اطلاعات سامانه‌ی غذا با موفقیت تغییر کرد', 'color': '#39b54a',
                           'username': request.user, 'coin': a})
