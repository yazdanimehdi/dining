from django.shortcuts import render, redirect

from dining.models import CustomUser, Coins


def dashboard(request):
    if request.user.is_authenticated:
        u = CustomUser.objects.get(username=request.user)
        a = Coins.objects.filter(user=request.user, active=True).count()
        return render(request, 'dining/templates/dashboard.html', {'username': u.username, 'coin': a})
    else:
        redirect("/login")


