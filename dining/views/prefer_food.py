from django.shortcuts import render, redirect

from dining.models import Food, UserDiningData, UserPreferableFood


def prefer_food(request):
    if request.user.is_authenticated:
        if not UserPreferableFood.objects.filter(user=request.user).exists():
            u = UserDiningData.objects.get(user=request.user)
            food_list = list()
            for foods in Food.objects.filter(university=u.university):
                food_list.append(foods.name)
            if request.method == 'GET':
                return render(request, 'dining/templates/prefered_food.html',
                              {'food_list': food_list, 'count': len(food_list)})
            elif request.method == 'POST':
                try:
                    for food in food_list:
                        d = UserPreferableFood()
                        d.user = request.user
                        d.food = Food.objects.get(name=food)
                        d.score = request.POST.get(food)
                        d.save()
                    return redirect('/self_select')
                except:
                    return render(request, 'dining/templates/prefered_food.html',
                                  {'food_list': food_list, 'count': len(food_list),
                                   'msg': 'یه چیزی اشتباه شد دوباره تلاش کن'})
        else:
            return redirect('/prefered_food/change')
