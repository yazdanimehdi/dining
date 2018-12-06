from django.shortcuts import render, redirect

from dining.models import UserDiningData


def userdiningdata_wizard(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'dining/templates/register_wizard.html')
        elif request.method == 'POST':
            try:
                u = UserDiningData.objects.get(user=request.user)
                for x in request.POST:
                    if hasattr(u, x):
                        u.__setattr__(x, request.POST.get(x))
                u.save()
            except:
                return render(request, 'dining/templates/register_wizard.html', {'msg': 'یه چیزی اشتباه پیش رفت'})
            return redirect('/prefered_food')
    else:
        return redirect('/login')