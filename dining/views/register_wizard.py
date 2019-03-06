from django.shortcuts import render, redirect

from dining.models import UserDiningData, UserSelfs


def get_scores_sharif(cookies):
    import requests
    import grequests
    import re
    from bs4 import BeautifulSoup

    url = 'http://dining.sharif.ir/admin/food/food-reserve/reserve'
    url_reserved_table = 'http://dining.sharif.ir/admin/food/food-reserve/load-reserved-table'
    result = requests.get(url, cookies=cookies)
    regex_find = re.findall(r'load_diet_reserve_table\((.*)\);\">هفته بعد', result.text)
    if regex_find:
        user_id = re.findall(r'\,(\d\d+)', regex_find[0])[0]
    else:
        return None

    k = 0
    rs = []
    score = {}
    while k < 100:
        rs.append({
            'week': f'-{k}',
            'user_id': user_id
        })
        k += 1
    requests = (grequests.post(url_reserved_table, data=data, cookies=cookies) for data in rs)
    results = grequests.map(requests)

    for result in results:
        soup = BeautifulSoup(result.text, 'html.parser')
        soup_find = soup.find_all('tr')
        soup_find.pop(0)

        data_lunch = dict()
        data_dinner = dict()
        for row in soup_find:
            day = re.findall(r'<th>\s+(.*?)\s\s', str(row))
            food_names_lunch = re.findall(r'<span>(.+?)<\/span>', str(row.find_all('td')[0]))
            food_names_dinner = re.findall(r'<span>(.+?)<\/span>', str(row.find_all('td')[1]))
            i = 0
            foods = []
            if food_names_dinner:
                for food in food_names_dinner:
                    if '<span class="label label-warning food_reserve_label">(نیمه تعطیل)</span>' in food:
                        food = \
                            food.split(
                                '<span class="label label-warning food_reserve_label">(نیمه تعطیل)</span>')[
                                0].strip()
                    foods.append(food)
                    i += 1
                data_dinner[day[0]] = foods
            else:
                data_dinner[day[0]] = '-'

            i = 0
            foods = []
            if food_names_lunch:
                for food in food_names_lunch:
                    if '<span class="label label-warning food_reserve_label">(نیمه تعطیل)</span>' in food:
                        food = \
                            food.split(
                                '<span class="label label-warning food_reserve_label">(نیمه تعطیل)</span>')[
                                0].strip()
                    foods.append(food)
                    i += 1
                data_lunch[day[0]] = foods
            else:
                data_lunch[day[0]] = '-'

        for item in data_lunch:
            if data_lunch[item][0] in score:
                score[data_lunch[item][0]] += 1
            else:
                score[data_lunch[item][0]] = 1
        k += 1
    total = 0
    del score['-']
    for food in score:
        total += score[food]

    for food in score:
        score[food] = score[food] / total

    food_list = []
    for food in score:
        food_list.append((food, score[food]))

    food_list.sort(key=lambda x: x[1], reverse=True)
    scores = []
    for item in food_list:
        scores.append((item[0], round((item[1] / food_list[0][1]) * 10)))

    return scores


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
                if not UserDiningData.objects.filter(dining_username=u.dining_username):
                    a, cookie = u.test_account()
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
                else:
                    return render(request, 'dining/templates/register_wizard.html',
                                  {'msg': 'نام کاربری سامانه‌ی غذا قبلا ثبت شده'})

            except ValueError:
                return render(request, 'dining/templates/register_wizard.html', {'msg': 'یه چیزی اشتباه پیش رفت'})
            request.session['scores'] = get_scores_sharif(cookie)
            return redirect('/prefered_food')
    else:
        return redirect('/login')