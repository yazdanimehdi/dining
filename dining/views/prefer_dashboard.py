from django.shortcuts import render,redirect
from dining.models import Food, UserDiningData, UserPreferableFood


def prefer_food_dashboard(request):
    if request.user.is_authenticated:
        u = UserDiningData.objects.get(user=request.user)
        food_list = list()
        for foods in Food.objects.filter(university=u.university):
            food_list.append(foods.name)
        if request.method == 'GET':
            print(food_list)
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
            return redirect('/')






