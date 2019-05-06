from django.shortcuts import render

from order.models import RestaurantMenu


def active(request):
    if request.method == 'GET':
        menu = RestaurantMenu.objects.filter(restaurant__name='RadBanoo').order_by('-price')
        context = {'foods': menu}
        return render(request, 'order/templates/ative_food.html', context)
    elif request.method == 'POST':
        for x in request.POST:
            if x != 'csrfmiddlewaretoken':
                food = RestaurantMenu.objects.get(id=x)
                if request.POST.get(x) == 'True':
                    food.is_active = True
                else:
                    food.is_active = False
                food.save()
        menu = RestaurantMenu.objects.filter(restaurant__name='RadBanoo')
        context = {'foods': menu}
        return render(request, 'order/templates/ative_food.html', context)
