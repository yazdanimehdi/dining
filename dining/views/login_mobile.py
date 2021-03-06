from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect


def login_mobile(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, "dining/templates/login_mobile.html")
        if not request.user.is_authenticated:
            if request.method == 'POST':
                username = request.POST.get('username')
                password = request.POST.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    auth_login(request, user)
                    return redirect('/dashboard_mobile')
                else:
                    return render(request, "dining/templates/login_mobile.html",
                                  {'msg': 'نام کاربری یا رمز عبور اشتباه است'})
            else:
                return render(request, "dining/templates/login_mobile.html",
                              {'msg': 'نام کاربری یا رمز عبور اشتباه است'})
        else:
            return redirect('/dashboard_mobile')
    else:
        return redirect('/dashboard_mobile')
