from django.shortcuts import render

from dining.models import UserDiningData


def change_info_dining(request):
    if request.user.is_authenticated:
        u = UserDiningData.objects.get(user=request.user)
        if request.method == 'GET':
            return render(request, 'dining/templates/change_info_dining .html',
                          {'username': u.dining_username,
                           'password': u.dining_password})
        elif request.method == 'POST':
            try:
                u.dining_username = request.POST.get('dining_username')
                u.dining_password = request.POST.get('dining_password')
                u.save()
            except:
                return render(request, 'dining/templates/change_info_dining .html',
                              {'username': u.dining_username,
                               'password': u.dining_password,
                               'msg': 'یه مشکلی پیش اومده دوباره تلاش کن'})

            return render(request, 'dining/templates/dashboard.html',
                          {'msg': ' !اطلاعات سامانه‌ی غذا با موفقیت تغییر کرد', 'color': '#39b54a',
                           'username': request.user})
