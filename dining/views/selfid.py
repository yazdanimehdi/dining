from django.shortcuts import render, redirect

from dining.models import UserSelfs, CustomUser


def self_id(request):
    if request.user.is_authenticated:
        a = UserSelfs.objects.filter(user=CustomUser.objects.get(username=request.user))
        self_list = list()
        for item in a:
            self_list.append(item.self_name)
        if request.method == 'GET':
            return render(request, 'dining/templates/self_selection.html', {'self_names': self_list})
        elif request.method == 'POST':
            user_self_names = dict(request.POST)
            user_self_names.pop('csrfmiddlewaretoken')
            for selfname in user_self_names:
                try:
                    self = UserSelfs.objects.get(user=request.user, self_name=selfname)
                    self.is_active = False
                    self.is_active = request.POST.get(selfname)
                    self.save()
                except:
                    return render(request, 'dining/templates/self_selection.html',
                                  {'self_names': self_list, 'msg': 'خطا!'})
            return redirect('/payment')
