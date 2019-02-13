from django.shortcuts import render, redirect

from dining.models import UserDiningData, UserSelfs


def userdiningdata_wizard_samad(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'dining/templates/register_wizard_samad.html')
        elif request.method == 'POST':
            try:
                u = UserDiningData.objects.get(user=request.user)
                for x in request.POST:
                    if hasattr(u, x):
                        u.__setattr__(x, request.POST.get(x))
                if not UserDiningData.objects.filter(dining_username=u.dining_username):
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
                        return render(request, 'dining/templates/register_wizard_samad.html',
                                      {'msg': 'نام کاربری یا رمز عبور سامانه‌ی غذا اشتباه مي‌باشد'})
                else:
                    return render(request, 'dining/templates/register_wizard_samad.html',
                                  {'msg': 'نام کاربری سامانه‌ی غذا قبلا ثبت شده'})
            except Exception as e:
                print(e)
                return render(request, 'dining/templates/register_wizard_samad.html', {'msg': 'یه چیزی اشتباه پیش رفت'})
            return redirect('/self_select')
        else:
            return redirect('/login')
