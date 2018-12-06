from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from dining.models import CustomUser, UserDiningData, University
from django.contrib.auth import authenticate, login as auth_login


def signup(request):
    if not request.user.is_authenticated:
        university_list = list()
        for item in University.objects.all():
            university_list.append(item.__getattribute__('name'))
        if request.method == "GET":
            return render(request, "dining/templates/register.html", {'university': university_list})
        elif request.method == "POST":
            u = CustomUser()
            d = UserDiningData()
            try:
                u.first_name = request.POST.get('first_name')
                u.last_name = request.POST.get('last_name')
                u.phone = request.POST.get('phone')
                u.username = request.POST.get('username')
                u.sex = request.POST.get('sex')
                if request.POST.get('password1') == request.POST.get('password2'):
                    u.set_password(request.POST.get('password1'))
                else:
                    return render(request, "dining/templates/register.html", {'msg': "!رمزعبور با هم هم‌خوانی ندارد", 'university': university_list})
            except:
                return render(request, "dining/templates/register.html", {'msg':"!برای ثبت‌نام تمامی فیلد‌ها باید پر گرددند", 'university': university_list})

            u.save()
            d.user = CustomUser.objects.get(username=request.POST.get('username'))
            d.university = University.objects.get(name=request.POST.get('university'))
            d.save()
            auth_login(request, u)
            return redirect('/wizard')
    else:
        if request.method == "GET":
            return redirect('/dashboard')
        else:
            return HttpResponseForbidden()

