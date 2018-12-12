from django.shortcuts import render, redirect

from dining.models import CustomUser, Coins


def dashboard(request):
    if request.user.is_authenticated:
        u = CustomUser.objects.get(username=request.user)
        a = Coins.objects.filter(user=request.user, active=True).count()
        if u.is_paid:
            msgp = '.حساب کاربریت فعاله'
            colorp = '#39b54a'
        else:
            msgp = '.حساب کاربریت غیره فعاله همین الان پرداخت کن'
            colorp = '#CE272D'
        return render(request, 'dining/templates/dashboard.html',
                      {'username': u.username, 'coin': a, 'msgp': msgp, 'colorp': colorp})
    else:
        return redirect("/login")
