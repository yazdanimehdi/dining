from django.shortcuts import render

from dining.models import Food, UserDiningData, UserPreferableFood, Coins


def prefer_food_dashboard(request):
    if request.user.is_authenticated:
        u = UserDiningData.objects.get(user=request.user)
        a = Coins.objects.filter(user=request.user, active=True).count()
        food_list = list()
        for foods in Food.objects.filter(university=u.university):
            food_list.append(foods.name)
        if request.method == 'GET':
            return render(request, 'dining/templates/prefered_food_dashboard_change.html', {'food_list': food_list})
        elif request.method == 'POST':
            food = Food.objects.get(name=request.POST.get('food_select'))
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
