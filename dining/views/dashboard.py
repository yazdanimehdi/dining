from django.shortcuts import render, redirect
from dining.models import CustomUser


def dashboard(request):
    if request.user.is_authenticated:
        u = CustomUser.objects.get(username=request.user)
        return render(request, 'dining/templates/dashboard.html', {'username': u.username})
    else:
        redirect("/login")


