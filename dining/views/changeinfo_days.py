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
                # Breakfast data
                u.reserve_sunday_breakfast = request.POST.get('reserve_sunday_breakfast')
                u.reserve_monday_breakfast = request.POST.get('reserve_monday_breakfast')
                u.reserve_tuesday_breakfast = request.POST.get('reserve_tuesday_breakfast')
                u.reserve_wednesday_breakfast = request.POST.get('reserve_wednesday_breakfast')
                u.reserve_thursday_breakfast = request.POST.get('reserve_thursday_breakfast')
                u.reserve_friday_breakfast = request.POST.get('reserve_friday_breakfast')
                u.reserve_saturday_breakfast = request.POST.get('reserve_saturday_breakfast')
                # lunch data
                u.reserve_sunday_lunch = request.POST.get('reserve_sunday_lunch')
                u.reserve_monday_lunch = request.POST.get('reserve_monday_lunch')
                u.reserve_tuesday_lunch = request.POST.get('reserve_tuesday_lunch')
                u.reserve_wednesday_lunch = request.POST.get('reserve_wednesday_lunch')
                u.reserve_thursday_lunch = request.POST.get('reserve_thursday_lunch')
                u.reserve_friday_lunch = request.POST.get('reserve_friday_lunch')
                u.reserve_saturday_lunch = request.POST.get('reserve_saturday_lunch')
                # dinner data
                u.reserve_sunday_dinner = request.POST.get('reserve_sunday_dinner')
                u.reserve_monday_dinner = request.POST.get('reserve_monday_dinner')
                u.reserve_tuesday_dinner = request.POST.get('reserve_tuesday_dinner')
                u.reserve_wednesday_dinner = request.POST.get('reserve_wednesday_dinner')
                u.reserve_thursday_dinner = request.POST.get('reserve_thursday_dinner')
                u.reserve_friday_dinner = request.POST.get('reserve_friday_dinner')
                u.reserve_saturday_dinner = request.POST.get('reserve_saturday_dinner')
                u.save()
            except:
                return render(request, 'dining/templates/change_days.html',
                              {'msg': 'یه چیزی اشتباه پیش رفت', 'coin': a})
            return render(request, 'dining/templates/dashboard.html',
                          {'msg': ' !روزها با موفقیت تغییر کرد', 'color': '#39b54a', 'username': request.user,
                           'coin': a})

    else:
        return redirect('/login')
