from django.shortcuts import render, redirect

from dining.models import Food, UserDiningData, UserPreferableFood


def prefer_food(request):
    if request.user.is_authenticated:
        if not UserPreferableFood.objects.filter(user=request.user).exists():
            u = UserDiningData.objects.filter(user=request.user)
            food_list = list()
            if request.method == 'GET':
                if u:
                    for foods in Food.objects.filter(university=u[0].university):
                        food_list.append(foods.name)
                    return render(request, 'dining/templates/prefered_food.html',
                                  {'food_list': food_list, 'count': len(food_list)})
                else:
                    return redirect('/wizard')
            elif request.method == 'POST':
                for foods in Food.objects.filter(university=u[0].university):
                    food_list.append(foods.name)
                try:
                    for food in food_list:
                        d = UserPreferableFood()
                        d.user = request.user
                        d.food = Food.objects.get(name=food)
                        if not request.POST.get(food):
                            d.score = 5
                        else:
                            d.score = request.POST.get(food)
                        d.save()
                    if u[0].university.tag == 'sharif':
                        return redirect('/self_select')
                    else:
                        return redirect('/payment')
                except Exception as e:
                    print(e)
                    return render(request, 'dining/templates/prefered_food.html',
                                  {'food_list': food_list, 'count': len(food_list),
                                   'msg': 'یه چیزی اشتباه شد دوباره تلاش کن'})
        else:
            return redirect('/prefered_food/change')
