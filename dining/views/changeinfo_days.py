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
                        u.reserve_saturday_lunch = False
                        u.reserve_sunday_lunch = False
                        u.reserve_monday_lunch = False
                        u.reserve_tuesday_lunch = False
                        u.reserve_wednesday_lunch = False
                        u.reserve_thursday_lunch = False
                        u.reserve_friday_lunch = False

                        u.reserve_saturday_breakfast = False
                        u.reserve_sunday_breakfast = False
                        u.reserve_monday_breakfast = False
                        u.reserve_tuesday_breakfast = False
                        u.reserve_wednesday_breakfast = False
                        u.reserve_thursday_breakfast = False
                        u.reserve_friday_breakfast = False

                        u.reserve_saturday_dinner = False
                        u.reserve_sunday_dinner = False
                        u.reserve_monday_dinner = False
                        u.reserve_tuesday_dinner = False
                        u.reserve_wednesday_dinner = False
                        u.reserve_thursday_dinner = False
                        u.reserve_friday_dinner = False

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
