from django.shortcuts import render, redirect

from dining.models import UserDiningData, Coins


def change_days(request):
    if request.user.is_authenticated:
        c = UserDiningData.objects.filter(user=request.user)
        if request.method == 'GET':
            if c:
                return render(request, 'dining/templates/change_days.html')
            else:
                return redirect('/wizard')
        elif request.method == 'POST':
            a = Coins.objects.filter(user=request.user, active=True).count()

            try:
                u = UserDiningData.objects.get(user=request.user)
                for x in request.POST:
                    if hasattr(u, x):
                        u.__setattr__(x, request.POST.get(x))
                u.save()
            except:
                return render(request, 'dining/templates/change_days.html',
                              {'msg': 'یه چیزی اشتباه پیش رفت', 'coin': a})
            return render(request, 'dining/templates/dashboard.html',
                          {'msg': ' !روزها با موفقیت تغییر کرد', 'color': '#39b54a', 'username': request.user,
                           'coin': a})

    else:
        return redirect('/login')
