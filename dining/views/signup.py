from django.contrib.auth import login as auth_login
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from dining.models import CustomUser, UserDiningData, University, Coins


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
            coin = Coins()
            try:
                u.first_name = request.POST.get('first_name')
                u.last_name = request.POST.get('last_name')
                u.phone = request.POST.get('phone')
                if not request.POST.get('phone'):
                    raise ValueError
                u.username = request.POST.get('username')
                u.email = request.POST.get('email')
                if not request.POST.get('email'):
                    raise ValueError
                u.sex = request.POST.get('sex')
                if request.POST.get('password1') == request.POST.get('password2'):
                    u.set_password(request.POST.get('password1'))
                else:
                    return render(request, "dining/templates/register.html", {'msg': "!رمزعبور با هم هم‌خوانی ندارد", 'university': university_list})
            except:
                return render(request, "dining/templates/register.html", {'msg':"!برای ثبت‌نام تمامی فیلد‌ها باید پر گرددند", 'university': university_list})
            if request.POST.get('agree-term') == 'on':
                if not CustomUser.objects.filter(username=u.username):
                    u.save()
                    d.user = CustomUser.objects.get(username=request.POST.get('username'))
                    d.university = University.objects.get(name=request.POST.get('university'))
                    d.save()
                    if 'introduced_user' in request.POST:
                        if (request.POST.get('introduced_user'),) in list(
                                CustomUser.objects.all().values_list('username')):
                            coin.user = CustomUser.objects.get(username=request.POST.get('introduced_user'))
                            coin.introduced_user = CustomUser.objects.get(username=request.POST.get('username'))
                            coin.save()
                    auth_login(request, u)
                    if University.objects.get(name=request.POST.get('university')).tag == 'sharif':
                        return redirect('/wizard')
                    else:
                        return redirect('/samad_wizard')
                else:
                    return render(request, "dining/templates/register.html",
                                  {'msg': "!این نام کاربری قبلا استفاده شده", 'university': university_list})
            else:
                return render(request, "dining/templates/register.html",
                              {'msg': "!موافقت با قوانین الزامی است", 'university': university_list})
    else:
        if request.method == "GET":
            return redirect('/dashboard')
        else:
            return HttpResponseForbidden()

