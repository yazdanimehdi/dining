from django.shortcuts import render, redirect, HttpResponse

from dining.models import CustomUser, Coins, MerchantUser


def dashboard_mobile(request):
    if request.user.is_authenticated:
        u = CustomUser.objects.get(username=request.user)
        a = Coins.objects.filter(user=request.user, active=True)
        coins = a.count()
        user_list = list()
        m = MerchantUser.objects.filter(user=request.user)
        m_list = list()

        for merchant in m:
            if merchant.active:
                m_list.append((merchant.merchant.name, merchant.code, merchant.merchant.address, '#39b54a'))
            else:
                m_list.append((merchant.merchant.name, merchant.code, merchant.merchant.address, '#CE272D'))
        for objects in a:
            user_list.append(objects.introduced_user)

        if u.is_paid:
            msgp = '.حساب کاربریت فعاله'
            colorp = '#39b54a'
        else:
            msgp = '.حساب کاربریت غیر فعاله همین الان پرداخت کن'
            colorp = '#CE272D'
        return render(request, 'dining/templates/dashboard_mobile.html',
                      {'username': u.username, 'coin': coins, 'msgp': msgp, 'colorp': colorp, 'users': user_list,
                       'merchants': m_list, })
    else:
        return redirect("/login_mobile")


def dashboard_request(request):
    if request.user.is_authenticated:
        u = CustomUser.objects.get(username=request.user)
        return HttpResponse(u.username)
