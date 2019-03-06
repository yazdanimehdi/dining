from django.shortcuts import render, redirect

from dining.models import Food, UserDiningData, UserPreferableFood


def prefer_food(request):
    if request.user.is_authenticated:
        if not UserPreferableFood.objects.filter(user=request.user).exists():
            u = UserDiningData.objects.filter(user=request.user)
            food_list = list()
            if request.method == 'GET':
                if u:
                    if u[0].university.tag == 'sharif':
                        msg = 'ما با توجه به سابقه‌ی رزروت این نمرات رو برای غذاها بهت پیشنهاد دادیم ' \
                              'اگر بخوای می‌تونی' \
                              ' به راحتی عوضشون کنی'
                        scores = request.session['scores']
                        for foods in Food.objects.filter(university=u[0].university):
                            food_list.append(foods.name)
                        if scores is not None:
                            for food in food_list:
                                flag = True
                                for item in scores:
                                    if item[0] == food:
                                        flag = False
                                if flag:
                                    scores.append((food, 0))
                        else:
                            for foods in Food.objects.filter(university=u[0].university):
                                scores.append((foods.name, 5))
                    else:
                        scores = []
                        msg = ''
                        for foods in Food.objects.filter(university=u[0].university):
                            scores.append((foods.name, 5))

                    return render(request, 'dining/templates/prefered_food.html',
                                  {'food_list': scores, 'count': len(food_list),
                                   'msg': msg})
                else:
                    return redirect('/wizard')
            elif request.method == 'POST':
                for foods in Food.objects.filter(university=u[0].university):
                    food_list.append(foods.name)
                try:
                    for food in food_list:
                        d = UserPreferableFood()
                        d.user = request.user
                        d.food = Food.objects.filter(name=food, university=u[0].university)[0]
                        if not request.POST.get(food):
                            d.score = 5
                        else:
                            d.score = request.POST.get(food)
                        d.save()
                    if u[0].university.tag == 'sharif':
                        return redirect('/self_select')
                    else:
                        request.user.is_paid = True
                        request.user.save()
                        return redirect('/dashboard')
                except Exception as e:
                    print(e)
                    return render(request, 'dining/templates/prefered_food.html',
                                  {'food_list': food_list, 'count': len(food_list),
                                   'msg': 'یه چیزی اشتباه شد دوباره تلاش کن'})
        else:
            return redirect('/prefered_food/change')
