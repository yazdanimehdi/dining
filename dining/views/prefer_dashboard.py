from django.shortcuts import render, redirect

from dining.models import Food, UserDiningData, UserPreferableFood, Coins


def prefer_food_dashboard(request):
    if request.user.is_authenticated:

        a = Coins.objects.filter(user=request.user, active=True).count()
        p = UserPreferableFood.objects.filter(user=request.user).count()
        food_list = list()
        u = UserDiningData.objects.get(user=request.user)
        if request.method == 'GET':
            if p != 0:
                u = UserDiningData.objects.get(user=request.user)
                for foods in Food.objects.filter(university=u.university):
                    food_list.append(foods.name)
                return render(request, 'dining/templates/prefered_food_dashboard_change.html', {'food_list': food_list})
            else:
                return redirect('/prefered_food')
        elif request.method == 'POST':
            print(request.POST)
            print(request.POST.get('food_select'))
            food = Food.objects.get(name=request.POST.get('food_select'), university=u.university)
            score = request.POST.get('food_change')
            d = UserPreferableFood.objects.get_or_create(user=request.user,
                                                         food=food,
                                                         defaults={'score': score})
            if d[1]:
                d[0].score = score
                d[0].save()
            return render(request, 'dining/templates/dashboard.html',
                          {'msg': ' !اطلاعات ترجیحی با موفقیت تغییر کرد', 'color': '#39b54a', 'username': request.user,
                           'coin': a})
