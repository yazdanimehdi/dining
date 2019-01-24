from django.shortcuts import render, redirect

from dining.models import UserSelfs, SamadPrefrredDays


def samad_day_select(request):
    if request.user.is_authenticated:
        selfs = UserSelfs.objects.filter(user=request.user, is_active=True)
        self_list = list()
        for item in selfs:
            self_list.append((item.self_name, item.self_id))
        if request.method == 'GET':
            return render(request, 'dining/templates/select_days.html', {'active_self': self_list})
        elif request.method == 'POST':
            try:
                for item in selfs:
                    obj = SamadPrefrredDays.objects.filter(user=request.user, active_self=item)
                    print(request.POST)
                    print(request.POST.get('saturday_breakfast_self'))
                    print(item.self_id)
                    if not obj:
                        u = SamadPrefrredDays()
                        u.user = request.user
                        u.active_self = item
                        if request.POST.get('saturday_breakfast_self') == item.self_id:
                            u.reserve_saturday_breakfast = True
                        if request.POST.get('sunday_breakfast_self') == item.self_id:
                            u.reserve_sunday_breakfast = True
                        if request.POST.get('monday_breakfast_self') == item.self_id:
                            u.reserve_monday_breakfast = True
                        if request.POST.get('tuesday_breakfast_self') == item.self_id:
                            u.reserve_tuesday_breakfast = True
                        if request.POST.get('wednesday_breakfast_self') == item.self_id:
                            u.reserve_wednesday_breakfast = True
                        if request.POST.get('thursday_breakfast_self') == item.self_id:
                            u.reserve_thursday_breakfast = True
                        if request.POST.get('friday_breakfast_self') == item.self_id:
                            u.reserve_friday_breakfast = True

                        if request.POST.get('saturday_lunch_self') == item.self_id:
                            u.reserve_saturday_lunch = True
                        if request.POST.get('sunday_lunch_self') == item.self_id:
                            u.reserve_sunday_lunch = True
                        if request.POST.get('monday_lunch_self') == item.self_id:
                            u.reserve_monday_lunch = True
                        if request.POST.get('tuesday_lunch_self') == item.self_id:
                            u.reserve_tuesday_lunch = True
                        if request.POST.get('wednesday_lunch_self') == item.self_id:
                            u.reserve_wednesday_lunch = True
                        if request.POST.get('thursday_lunch_self') == item.self_id:
                            u.reserve_thursday_lunch = True
                        if request.POST.get('friday_lunch_self') == item.self_id:
                            u.reserve_friday_lunch = True

                        if request.POST.get('saturday_dinner_self') == item.self_id:
                            u.reserve_saturday_dinner = True
                        if request.POST.get('sunday_dinner_self') == item.self_id:
                            u.reserve_sunday_dinner = True
                        if request.POST.get('monday_dinner_self') == item.self_id:
                            u.reserve_monday_dinner = True
                        if request.POST.get('tuesday_dinner_self') == item.self_id:
                            u.reserve_tuesday_dinner = True
                        if request.POST.get('wednesday_dinner_self') == item.self_id:
                            u.reserve_wednesday_dinner = True
                        if request.POST.get('thursday_dinner_self') == item.self_id:
                            u.reserve_thursday_dinner = True
                        if request.POST.get('friday_dinner_self') == item.self_id:
                            u.reserve_friday_dinner = True

                        u.save()
                    else:
                        if request.POST.get('saturday_breakfast_self') == item.self_id:
                            obj[0].reserve_saturday_breakfast = True
                        if request.POST.get('sunday_breakfast_self') == item.self_id:
                            obj[0].reserve_sunday_breakfast = True
                        if request.POST.get('monday_breakfast_self') == item.self_id:
                            obj[0].reserve_monday_breakfast = True
                        if request.POST.get('tuesday_breakfast_self') == item.self_id:
                            obj[0].reserve_tuesday_breakfast = True
                        if request.POST.get('wednesday_breakfast_self') == item.self_id:
                            obj[0].reserve_wednesday_breakfast = True
                        if request.POST.get('thursday_breakfast_self') == item.self_id:
                            obj[0].reserve_thursday_breakfast = True
                        if request.POST.get('friday_breakfast_self') == item.self_id:
                            obj[0].reserve_friday_breakfast = True

                        if request.POST.get('saturday_lunch_self') == item.self_id:
                            obj[0].reserve_saturday_lunch = True
                        if request.POST.get('sunday_lunch_self') == item.self_id:
                            obj[0].reserve_sunday_lunch = True
                        if request.POST.get('monday_lunch_self') == item.self_id:
                            obj[0].reserve_monday_lunch = True
                        if request.POST.get('tuesday_lunch_self') == item.self_id:
                            obj[0].reserve_tuesday_lunch = True
                        if request.POST.get('wednesday_lunch_self') == item.self_id:
                            obj[0].reserve_wednesday_lunch = True
                        if request.POST.get('thursday_lunch_self') == item.self_id:
                            obj[0].reserve_thursday_lunch = True
                        if request.POST.get('friday_lunch_self') == item.self_id:
                            obj[0].reserve_friday_lunch = True

                        if request.POST.get('saturday_dinner_self') == item.self_id:
                            obj[0].reserve_saturday_dinner = True
                        if request.POST.get('sunday_dinner_self') == item.self_id:
                            obj[0].reserve_sunday_dinner = True
                        if request.POST.get('monday_dinner_self') == item.self_id:
                            obj[0].reserve_monday_dinner = True
                        if request.POST.get('tuesday_dinner_self') == item.self_id:
                            obj[0].reserve_tuesday_dinner = True
                        if request.POST.get('wednesday_dinner_self') == item.self_id:
                            obj[0].reserve_wednesday_dinner = True
                        if request.POST.get('thursday_dinner_self') == item.self_id:
                            obj[0].reserve_thursday_dinner = True
                        if request.POST.get('friday_dinner_self') == item.self_id:
                            obj[0].reserve_friday_dinner = True

                        obj[0].save()
                return redirect('/prefered_food')
            except:
                return render(request, 'dining/templates/select_days.html',
                              {'active_self': self_list, 'msg': 'یه چیزی اشتباه پیش رفت دوباره تلاش کن'})
