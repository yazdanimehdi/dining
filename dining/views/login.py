from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect


def login(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, "dining/templates/login.html")
        if not request.user.is_authenticated:
            if request.method == 'POST':
                username = request.POST.get('username')
                password = request.POST.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    return redirect('/dashboard')
                else:
                    return render(request, "dining/templates/login.html", {'msg': 'نام کاربری یا رمز عبور اشتباه است'})
            else:
                return render(request, "dining/templates/login.html", {'msg': 'نام کاربری یا رمز عبور اشتباه است'})
        else:
            return redirect('/dashboard')
    else:
        return redirect('/dashboard')
