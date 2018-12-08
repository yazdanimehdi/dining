from django.shortcuts import render

from dining.models import CustomUser, Coins


def change_info(request):
    if request.user.is_authenticated:
        a = Coins.objects.filter(user=request.user, active=True).count()
        u = CustomUser.objects.get(username=request.user)
        if request.method == 'GET':
            return render(request, 'dining/templates/change_info.html',
                          {'firstname': u.first_name,
                           'lastname': u.last_name,
                           'email': u.email,
                           'phone': u.phone})
        elif request.method == 'POST':
            try:
                u.first_name = request.POST.get('first_name')
                u.last_name = request.POST.get('last_name')
                u.email = request.POST.get('email')
                u.phone = request.POST.get('phone')
                u.save()
            except:
                return render(request, 'dining/templates/change_info.html',
                              {'firstname': u.first_name,
                               'lastname': u.last_name,
                               'email': u.email,
                               'phone': u.phone,
                               'msg': 'یه مشکلی پیش اومده دوباره تلاش کن'})

            return render(request, 'dining/templates/dashboard.html',
                          {'msg': ' !اطلاعات شخصی با موفقیت تغییر کرد', 'color': '#39b54a', 'username': request.user,
                           'coin': a})
