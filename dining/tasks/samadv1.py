import re

import requests
from bs4 import BeautifulSoup
from celery import task
from django.db.models import Q
from lxml import html


@task()
def samadv1_reserve_function():
    from dining.models import UserDiningData, UserSelfs, UserPreferableFood, SamadPrefrredDays, Food, \
        University
    for user_data in UserDiningData.objects.filter(university__tag='samadv1'):
        if user_data.user.is_paid:
            try:
                alert = []
                print(user_data.university, user_data.user)
                login_url = user_data.university.login_url
                reserve_get_url = user_data.university.reserve_url
                simple = user_data.university.simple_url
                for self in UserSelfs.objects.filter(user=user_data.user, is_active=True):
                    session_requests = requests.session()
                    result = session_requests.get(login_url, verify=False)
                    tree = html.fromstring(result.text)
                    authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
                    payload = {
                        'username': user_data.dining_username,
                        'password': user_data.dining_password,
                        '_csrf': authenticity_token,
                        'login': 'ورود'
                    }

                    result = session_requests.post(login_url, data=payload, verify=False)
                    result = session_requests.get(reserve_get_url, verify=False)
                    tree = html.fromstring(result.text)
                    result = session_requests.get(
                        f'{simple}/nurture/user/multi/reserve/showPanel.rose?selectedSelfDefId={self.self_id}',
                        verify=False)
                    tree = html.fromstring(result.text)
                    authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
                    weekStartDateTime = list(set(tree.xpath("//input[@name='weekStartDateTime']/@value")))[0]
                    weekStartDateTimeAjx = list(set(tree.xpath("//input[@name='weekStartDateTimeAjx']/@value")))[0]
                    remainCredit = list(set(tree.xpath("//input[@name='remainCredit']/@value")))[0]
                    payload_reserve = {
                        'method:showNextWeek': 'Submit',
                        'weekStartDateTime': weekStartDateTime,
                        'remainCredit': remainCredit,
                        'selfChangeReserveId': '',
                        'weekStartDateTimeAjx': weekStartDateTimeAjx,
                        'selectedSelfDefId': self.self_id,
                        '_csrf': authenticity_token,
                    }
                    tree = html.fromstring(result.text)
                    soup = BeautifulSoup(result.text, 'html.parser')
                    soup_find = soup.findAll('tr')[2].findAll('tr')
                    i = 0
                    a_index = list()
                    for tr in soup_find:
                        a = re.findall(r'شنبه', str(tr))
                        if a:
                            a_index.append(i)
                        i += 1
                    lunch_data = dict()
                    breakfast_data = dict()
                    dinner_data = dict()
                    j = 0
                    for i in a_index:
                        day = re.findall(
                            r'align=\"center\" style=\"background:#F0F0F0;border:1px solid #CCCCCC; border-top:none;\" valign=\"middle\" width=\"12%\">\s+(.*)\s+<br\/>',
                            str(soup_find[i]))[0].strip()
                        date = re.findall(r'<div>(.+)</div>', str(soup_find[i]))[0]
                        weekStartDateTime = \
                            list(set(tree.xpath("//*[@id=\"resFinalform_weekStartDateTime\"]/@value")))[
                                0]
                        weekStartDateTimeAjx = \
                            list(set(tree.xpath("//input[@name='weekStartDateTimeAjx']/@value")))[0]
                        foods_lunch = []
                        foods_dinner = []
                        foods_breakfast = []
                        for soupf in soup_find[i].find_all('tr'):
                            price_list = re.findall(r'class=\"xstooltip\".+\>\s+(.+)', str(soupf))[0]
                            programId = re.findall(r'programId\" type=\"hidden\" value=\"(.+)\"', str(soupf))[0]
                            mealTypeId = re.findall(r'mealTypeId\" type=\"hidden\" value=\"(.+)\"', str(soupf))[0]
                            programDateTime = \
                                re.findall(r'programDateTime\" type=\"hidden\" value=\"(.+)\"', str(soupf))[0]
                            foodTypeId = re.findall(r'foodTypeId\"\s+.+value=\"(.+)\"',
                                                    str(soupf))[0]
                            freeFoodSelected = \
                                re.findall(r'freeFoodSelected\" type=\"hidden\" value="(.+)\"', str(soupf))[
                                    0]
                            food_name = re.findall(r'this.offsetLeft, this.offsetTop\);\">\s+(.+)', str(soupf))[0]
                            if tree.xpath(f"//*[@id=\"userWeekReserves.selected{j}_hidden\"]/@value"):
                                selected = tree.xpath(f"//*[@id=\"userWeekReserves.selected{j}_hidden\"]/@value")[0]
                            else:
                                if 'null' in tree.xpath(f'//*[@id=\"userWeekReserves.selected{j}\"]/@onclick')[0]:
                                    selected = 'false'
                                else:
                                    selected = 'true'
                            if selected == 'true':
                                selected_count = 1
                            else:
                                selected_count = 0

                            if mealTypeId == '1':
                                foods_breakfast.append(
                                    (j, food_name, price_list, programId, mealTypeId, programDateTime,
                                     foodTypeId, freeFoodSelected, selected, selected_count))
                            if mealTypeId == '2':
                                foods_lunch.append(
                                    (j, food_name, price_list, programId, mealTypeId, programDateTime,
                                     foodTypeId, freeFoodSelected, selected, selected_count))
                            if mealTypeId == '3':
                                foods_dinner.append(
                                    (j, food_name, price_list, programId, mealTypeId, programDateTime,
                                     foodTypeId, freeFoodSelected, selected, selected_count))
                            j += 1

                        lunch_data[(day, date)] = foods_lunch
                        dinner_data[(day, date)] = foods_dinner
                        breakfast_data[(day, date)] = foods_breakfast
                        Credit = int(list(set(tree.xpath("//input[@name='remainCredit']/@value")))[0])

                        if lunch_data:
                            for item in lunch_data:
                                k = 0
                                while k < len(lunch_data[item]):
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].selected'] = \
                                        lunch_data[item][k][8]
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].id'] = ''
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].programId'] = \
                                        lunch_data[item][k][3]
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].mealTypeId'] = \
                                        lunch_data[item][k][4]
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].programDateTime'] = \
                                        lunch_data[item][k][5]
                                    payload_reserve[
                                        f'userWeekReserves[{lunch_data[item][k][0]}].selfId'] = self.self_id
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].foodTypeId'] = \
                                        lunch_data[item][k][6]
                                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].selectedCount'] = \
                                        lunch_data[item][k][9]
                                    payload_reserve[
                                        f'userWeekReserves[{lunch_data[item][k][0]}].freeFoodSelected'] = \
                                        lunch_data[item][k][7]
                                    k += 1

                        if breakfast_data:
                            for item in breakfast_data:
                                k = 0
                                while k < len(breakfast_data[item]):
                                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].selected'] = \
                                        breakfast_data[item][k][8]
                                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].id'] = ''
                                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].programId'] = \
                                        breakfast_data[item][k][3]
                                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].mealTypeId'] = \
                                        breakfast_data[item][k][4]
                                    payload_reserve[
                                        f'userWeekReserves[{breakfast_data[item][k][0]}].programDateTime'] = \
                                        breakfast_data[item][k][5]
                                    payload_reserve[
                                        f'userWeekReserves[{breakfast_data[item][k][0]}].selfId'] = self.self_id
                                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].foodTypeId'] = \
                                        breakfast_data[item][k][6]
                                    payload_reserve[
                                        f'userWeekReserves[{breakfast_data[item][k][0]}].selectedCount'] = \
                                        breakfast_data[item][k][9]
                                    payload_reserve[
                                        f'userWeekReserves[{breakfast_data[item][k][0]}].freeFoodSelected'] = \
                                        breakfast_data[item][k][7]
                                    k += 1
                        if dinner_data:
                            for item in dinner_data:
                                k = 0
                                while k < len(dinner_data[item]):
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].selected'] = \
                                        dinner_data[item][k][
                                            8]
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].id'] = ''
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].programId'] = \
                                        dinner_data[item][k][3]
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].mealTypeId'] = \
                                        dinner_data[item][k][4]
                                    payload_reserve[
                                        f'userWeekReserves[{dinner_data[item][k][0]}].programDateTime'] = \
                                        dinner_data[item][k][5]
                                    payload_reserve[
                                        f'userWeekReserves[{dinner_data[item][k][0]}].selfId'] = self.self_id
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].foodTypeId'] = \
                                        dinner_data[item][k][6]
                                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].selectedCount'] = \
                                        dinner_data[item][k][9]
                                    payload_reserve[
                                        f'userWeekReserves[{dinner_data[item][k][0]}].freeFoodSelected'] = \
                                        dinner_data[item][k][7]
                                    k += 1
                    result = session_requests.post(
                        reserve_get_url,
                        data=payload_reserve, verify=False)

                    tree = html.fromstring(result.text)
                    soup = BeautifulSoup(result.text, 'html.parser')
                    soup_find = soup.findAll('tr')[2].findAll('tr')
                    i = 0
                    a_index = list()
                    for tr in soup_find:
                        a = re.findall(r'شنبه', str(tr))
                        if a:
                            a_index.append(i)
                        i += 1
                    lunch_data = dict()
                    breakfast_data = dict()
                    dinner_data = dict()
                    j = 0
                    for i in a_index:
                        day = re.findall(
                            r'align=\"center\" style=\"background:#F0F0F0;border:1px solid #CCCCCC; border-top:none;\" valign=\"middle\" width=\"12%\">\s+(.*)\s+<br\/>',
                            str(soup_find[i]))[0].strip()
                        date = re.findall(r'<div>(.+)</div>', str(soup_find[i]))[0]
                        weekStartDateTime = \
                            list(set(tree.xpath("//*[@id=\"resFinalform_weekStartDateTime\"]/@value")))[
                                0]
                        weekStartDateTimeAjx = \
                            list(set(tree.xpath("//input[@name='weekStartDateTimeAjx']/@value")))[0]
                        foods_lunch = []
                        foods_dinner = []
                        foods_breakfast = []
                        for soupf in soup_find[i].find_all('tr'):
                            price_list = re.findall(r'class=\"xstooltip\".+\>\s+(.+)', str(soupf))[0]
                            programId = re.findall(r'programId\" type=\"hidden\" value=\"(.+)\"', str(soupf))[0]
                            mealTypeId = re.findall(r'mealTypeId\" type=\"hidden\" value=\"(.+)\"', str(soupf))[
                                0]
                            programDateTime = \
                                re.findall(r'programDateTime\" type=\"hidden\" value=\"(.+)\"', str(soupf))[0]
                            foodTypeId = re.findall(r'foodTypeId\"\s+.+value=\"(.+)\"',
                                                    str(soupf))[0]
                            freeFoodSelected = \
                                re.findall(r'freeFoodSelected\" type=\"hidden\" value="(.+)\"', str(soupf))[
                                    0]
                            food_name = re.findall(r'xstooltip_hide\(\'foodPriceTooltip.+\s+(.+)', str(soupf))
                            if food_name:
                                food_name = food_name[0].split('|')[1].strip()

                            if tree.xpath(f"//*[@id=\"userWeekReserves.selected{j}_hidden\"]/@value"):
                                selected = \
                                    tree.xpath(f"//*[@id=\"userWeekReserves.selected{j}_hidden\"]/@value")[0]
                            else:
                                if 'null' in tree.xpath(f'//*[@id=\"userWeekReserves.selected{j}\"]/@onclick')[
                                    0]:
                                    selected = 'false'
                                else:
                                    selected = 'true'
                            if selected == 'true':
                                selected_count = 1
                            else:
                                selected_count = 0
                            flag = False
                            for db_food in Food.objects.filter(university=user_data.university):
                                if set(db_food.name.split(' ')).issubset(food_name.split(' ')):
                                    flag = True
                                elif db_food.name in food_name:
                                    flag = True
                            if not flag:
                                uni = University.objects.get(name=user_data.university)
                                newfood = Food()
                                newfood.name = food_name
                                newfood.university = uni
                                newfood.save()
                                u = UserPreferableFood.objects.create(user=user_data.user, food=newfood,
                                                                      score=5)
                                u.save()
                                flag = True
                            if mealTypeId == '1':
                                foods_breakfast.append(
                                    (j, food_name, price_list, programId, mealTypeId, programDateTime,
                                     foodTypeId, freeFoodSelected, selected, selected_count))
                            if mealTypeId == '2':
                                foods_lunch.append(
                                    (j, food_name, price_list, programId, mealTypeId, programDateTime,
                                     foodTypeId, freeFoodSelected, selected, selected_count))
                            if mealTypeId == '3':
                                foods_dinner.append(
                                    (j, food_name, price_list, programId, mealTypeId, programDateTime,
                                     foodTypeId, freeFoodSelected, selected, selected_count))
                            j += 1

                        lunch_data[(day, date)] = foods_lunch
                        dinner_data[(day, date)] = foods_dinner
                        breakfast_data[(day, date)] = foods_breakfast
                    Credit = int(list(set(tree.xpath("//input[@name='remainCredit']/@value")))[0])
                    payload_reserve = {
                        'weekStartDateTime': weekStartDateTime,
                        'method:doReserve': 'Submit',
                        'selfChangeReserveId': '',
                        'weekStartDateTimeAjx': weekStartDateTimeAjx,
                        'selectedSelfDefId': self.self_id,
                        '_csrf': authenticity_token,
                    }

                    pdays = SamadPrefrredDays.objects.get(user=user_data.user, active_self=self)

                    chosen_days_breakfast = []
                    if pdays.reserve_friday_breakfast:
                        chosen_days_breakfast.append('جمعه')
                    if pdays.reserve_saturday_breakfast:
                        chosen_days_breakfast.append('شنبه')
                    if pdays.reserve_sunday_breakfast:
                        chosen_days_breakfast.append('یکشنبه')
                    if pdays.reserve_monday_breakfast:
                        chosen_days_breakfast.append('دوشنبه')
                    if pdays.reserve_tuesday_breakfast:
                        chosen_days_breakfast.append('سه شنبه')
                    if pdays.reserve_wednesday_breakfast:
                        chosen_days_breakfast.append('چهارشنبه')
                    if pdays.reserve_thursday_breakfast:
                        chosen_days_breakfast.append('پنجشنبه')

                    chosen_days_lunch = []

                    if pdays.reserve_friday_lunch:
                        chosen_days_lunch.append('جمعه')
                    if pdays.reserve_saturday_lunch:
                        chosen_days_lunch.append('شنبه')
                    if pdays.reserve_sunday_lunch:
                        chosen_days_lunch.append('یکشنبه')
                    if pdays.reserve_monday_lunch:
                        chosen_days_lunch.append('دوشنبه')
                    if pdays.reserve_tuesday_lunch:
                        chosen_days_lunch.append('سه شنبه')
                    if pdays.reserve_wednesday_lunch:
                        chosen_days_lunch.append('چهارشنبه')
                    if pdays.reserve_thursday_lunch:
                        chosen_days_lunch.append('پنجشنبه')

                    chosen_days_dinner = []

                    if pdays.reserve_friday_dinner:
                        chosen_days_dinner.append('جمعه')
                    if pdays.reserve_saturday_dinner:
                        chosen_days_dinner.append('شنبه')
                    if pdays.reserve_sunday_dinner:
                        chosen_days_dinner.append('یکشنبه')
                    if pdays.reserve_monday_dinner:
                        chosen_days_dinner.append('دوشنبه')
                    if pdays.reserve_tuesday_dinner:
                        chosen_days_dinner.append('سه شنبه')
                    if pdays.reserve_wednesday_lunch:
                        chosen_days_dinner.append('چهارشنبه')
                    if pdays.reserve_thursday_dinner:
                        chosen_days_dinner.append('پنجشنبه')

                    total_price = 0

                    if lunch_data:
                        for item in lunch_data:
                            k = 0
                            while k < len(lunch_data[item]):
                                payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].selected'] = \
                                    lunch_data[item][k][8]
                                payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].id'] = ''
                                payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].programId'] = \
                                    lunch_data[item][k][3]
                                payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].mealTypeId'] = \
                                    lunch_data[item][k][4]
                                payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].programDateTime'] = \
                                    lunch_data[item][k][5]
                                payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].selfId'] = self.self_id
                                payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].foodTypeId'] = \
                                    lunch_data[item][k][6]
                                payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].selectedCount'] = \
                                    lunch_data[item][k][9]
                                payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].freeFoodSelected'] = \
                                    lunch_data[item][k][7]
                                k += 1

                    if breakfast_data:
                        for item in breakfast_data:
                            k = 0
                            while k < len(breakfast_data[item]):
                                payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].selected'] = \
                                    breakfast_data[item][k][8]
                                payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].id'] = ''
                                payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].programId'] = \
                                    breakfast_data[item][k][3]
                                payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].mealTypeId'] = \
                                    breakfast_data[item][k][4]
                                payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].programDateTime'] = \
                                    breakfast_data[item][k][5]
                                payload_reserve[
                                    f'userWeekReserves[{breakfast_data[item][k][0]}].selfId'] = self.self_id
                                payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].foodTypeId'] = \
                                    breakfast_data[item][k][6]
                                payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].selectedCount'] = \
                                    breakfast_data[item][k][9]
                                payload_reserve[
                                    f'userWeekReserves[{breakfast_data[item][k][0]}].freeFoodSelected'] = \
                                    breakfast_data[item][k][7]
                                k += 1
                    if dinner_data:
                        for item in dinner_data:
                            k = 0
                            while k < len(dinner_data[item]):
                                payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].selected'] = \
                                    dinner_data[item][k][
                                        8]
                                payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].id'] = ''
                                payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].programId'] = \
                                    dinner_data[item][k][3]
                                payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].mealTypeId'] = \
                                    dinner_data[item][k][4]
                                payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].programDateTime'] = \
                                    dinner_data[item][k][5]
                                payload_reserve[
                                    f'userWeekReserves[{dinner_data[item][k][0]}].selfId'] = self.self_id
                                payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].foodTypeId'] = \
                                    dinner_data[item][k][6]
                                payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].selectedCount'] = \
                                    dinner_data[item][k][9]
                                payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].freeFoodSelected'] = \
                                    dinner_data[item][k][7]
                                k += 1

                        for daye in dinner_data:
                            if dinner_data[daye]:
                                for day in chosen_days_lunch:
                                    if daye[0] == day and (dinner_data[daye] != []):
                                        food_list = []
                                        for food in dinner_data[daye]:
                                            prefered_food = UserPreferableFood.objects.filter(~Q(score=0),
                                                                                              user=user_data.user,
                                                                                              food__name=food[1])
                                            if prefered_food:
                                                food_list.append((food[0],
                                                                  prefered_food[0],
                                                                  food[2]))
                                        food_list.sort(key=lambda x: x[1].score, reverse=True)
                                        prefered_data = food_list
                                        if prefered_data:
                                            try:
                                                tree = html.fromstring(result.text)
                                                Credit = int(
                                                    list(set(tree.xpath("//input[@name='remainCredit']/@value")))[0])
                                                payload_reserve[
                                                    f'userWeekReserves[{prefered_data[0][0]}].selected'] = 'true'
                                                payload_reserve[
                                                    f'userWeekReserves[{prefered_data[0][0]}].selectedCount'] = '1'

                                                a = int(prefered_data[0][2])
                                                total_price += a
                                                payload_reserve['remainCredit'] = Credit - total_price
                                                result = session_requests.post(reserve_get_url, data=payload_reserve)
                                            except:
                                                pass

                        for daye in lunch_data:
                            if lunch_data[daye]:
                                for day in chosen_days_lunch:
                                    if (daye[0] == day) and (lunch_data[daye] != []):
                                        food_list = []
                                        for food in lunch_data[daye]:
                                            prefered_food = UserPreferableFood.objects.filter(~Q(score=0),
                                                                                              user=user_data.user,
                                                                                              food__name=food[1])
                                            if prefered_food:
                                                food_list.append((food[0],
                                                                  prefered_food[0],
                                                                  food[2]))
                                        food_list.sort(key=lambda x: x[1].score, reverse=True)
                                        prefered_data = food_list
                                        if prefered_data:
                                            try:
                                                tree = html.fromstring(result.text)
                                                Credit = int(
                                                    list(set(tree.xpath("//input[@name='remainCredit']/@value")))[0])
                                                payload_reserve[
                                                    f'userWeekReserves[{prefered_data[0][0]}].selected'] = 'true'
                                                payload_reserve[
                                                    f'userWeekReserves[{prefered_data[0][0]}].selectedCount'] = '1'

                                                a = int(prefered_data[0][2])
                                                total_price += a
                                                payload_reserve['remainCredit'] = Credit - total_price
                                                result = session_requests.post(reserve_get_url, data=payload_reserve)
                                            except:
                                                pass

                        for daye in breakfast_data:
                            if breakfast_data[daye]:
                                for day in chosen_days_breakfast:
                                    if daye[0] == day and (breakfast_data[daye] != []):
                                        food_list = []
                                        for food in breakfast_data[daye]:
                                            prefered_food = UserPreferableFood.objects.filter(~Q(score=0),
                                                                                              user=user_data.user,
                                                                                              food__name=food[1])
                                            if prefered_food:
                                                food_list.append((food[0],
                                                                  prefered_food[0],
                                                                  food[2]))
                                        food_list.sort(key=lambda x: x[1].score, reverse=True)
                                        prefered_data = food_list
                                        if prefered_data:
                                            try:
                                                tree = html.fromstring(result.text)
                                                Credit = int(
                                                    list(set(tree.xpath("//input[@name='remainCredit']/@value")))[0])
                                                payload_reserve[
                                                    f'userWeekReserves[{prefered_data[0][0]}].selected'] = 'true'
                                                payload_reserve[
                                                    f'userWeekReserves[{prefered_data[0][0]}].selectedCount'] = '1'
                                                a = int(prefered_data[0][2])
                                                total_price += a
                                                payload_reserve['remainCredit'] = Credit - total_price
                                                result = session_requests.post(reserve_get_url, data=payload_reserve)
                                            except:
                                                pass

            except Exception as e:
                print(e)
