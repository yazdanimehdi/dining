from django.shortcuts import render, redirect

from dining.models import UserDiningData, UserSelfs


def userdiningdata_wizard(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'dining/templates/register_wizard.html')
        elif request.method == 'POST':
            print(request.POST)
            try:
                u = UserDiningData.objects.get(user=request.user)
                for x in request.POST:
                    if hasattr(u, x):
                        u.__setattr__(x, request.POST.get(x))
                a = u.test_account()
                if a != {}:
                    for item in a:
                        self = UserSelfs()
                        self.user = request.user
                        self.self_name = item
                        self.self_id = a[item]
                        self.save()
                    u.save()
                else:
                    return render(request, 'dining/templates/register_wizard.html',
                                  {'msg': 'نام کاربری یا رمز عبور سامانه‌ی غذا اشتباه مي‌باشد'})

            except ValueError:
                return render(request, 'dining/templates/register_wizard.html', {'msg': 'یه چیزی اشتباه پیش رفت'})
            return redirect('/prefered_food')
    else:
        return redirect('/login')