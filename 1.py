import re

import jdatetime
import requests
from bs4 import BeautifulSoup
from lxml import html

from dining.models import UserDiningData, ReservedTable, UserSelfs, UserPreferableFood, Food, SamadPrefrredDays

for user_data in UserDiningData.objects.filter(university__tag='samad'):
    if user_data.user.is_paid:

        login_url = user_data.university.login_url
        reserve_get_url = user_data.university.reserve_table
        csrf = user_data.university.csrf_name
        session_requests = requests.session()
        result = session_requests.get(login_url)

        tree = html.fromstring(result.text)
        authenticity_token = list(set(tree.xpath(f"//input[@name='{csrf}']/@value")))[0]
        payload = {
            user_data.university.form_username: user_data.dining_username,
            user_data.university.form_password: user_data.dining_password,
            csrf: authenticity_token,
        }

        result = session_requests.post(login_url, data=payload, headers=dict(referer=login_url))
        result = session_requests.get(reserve_get_url)

        tree = html.fromstring(result.text)
        authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
        weekStartDateTime = list(set(tree.xpath("//input[@name='weekStartDateTime']/@value")))[0]
        weekStartDateTimeAjx = list(set(tree.xpath("//input[@name='weekStartDateTimeAjx']/@value")))[0]
        remainCredit = list(set(tree.xpath("//input[@name='remainCredit']/@value")))[0]

        for self in UserSelfs.objects.filter(user=user_data.user, is_active=True):
            payload_load = {
                'method:showNextWeek': 'Submit',
                'weekStartDateTime': weekStartDateTime,
                'remainCredit': remainCredit,
                'selfChangeReserveId': '',
                'weekStartDateTimeAjx': weekStartDateTimeAjx,
                'selectedSelfDefId': self.self_id,
                '_csrf': authenticity_token,
            }
            result = session_requests.post(reserve_get_url, data=payload_load)
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
                    str(soup_find[i]))[0]
                date = re.findall(r'<div>(.+)</div>', str(soup_find[i]))[0]
                weekStartDateTime = list(set(tree.xpath("//*[@id=\"resFinalform_weekStartDateTime\"]/@value")))[
                    0]
                weekStartDateTimeAjx = list(set(tree.xpath("//input[@name='weekStartDateTimeAjx']/@value")))[0]
                foods_lunch = list()
                foods_dinner = list()
                foods_breakfast = list()
                for soupf in soup_find[i].find_all('tr'):
                    price_list = re.findall(r'class=\"xstooltip\".+\>\s+(.+)', str(soupf))[0]
                    programId = re.findall(r'programId\" type=\"hidden\" value=\"(.+)\"', str(soupf))[0]
                    mealTypeId = re.findall(r'mealTypeId\" type=\"hidden\" value=\"(.+)\"', str(soupf))[0]
                    programDateTime = \
                        re.findall(r'programDateTime\" type=\"hidden\" value=\"(.+)\"', str(soupf))[0]
                    foodTypeId = re.findall(
                        r'userWeekReserves\[.\]\.foodTypeId\" type=\"hidden\" value=\"(.+)\"',
                        str(soupf))
                    if foodTypeId:
                        foodTypeId = \
                            re.findall(r'userWeekReserves\[.\]\.foodTypeId\" type=\"hidden\" value=\"(.+)\"',
                                       str(soupf))[0]
                    else:
                        foodTypeId = '0'
                    freeFoodSelected = \
                        re.findall(r'freeFoodSelected\" type=\"hidden\" value="(.+)\"', str(soupf))[
                            0]
                    food_name = re.findall(r'this.offsetLeft, this.offsetTop\);\">\s+(.+)', str(soupf))[0]
                    flag = False
                    for db_food in UserPreferableFood.objects.filter(user=user_data.user):
                        if set(db_food.food.name.split(' ')).issubset(food_name.split(' ')):
                            food_name = db_food.food.name
                            flag = True
                        elif db_food.food.name in food_name:
                            food_name = db_food.food.name
                            flag = True
                        if flag:
                            if mealTypeId == '1':
                                foods_breakfast.append(
                                    (j, food_name, price_list, programId, mealTypeId, programDateTime,
                                     foodTypeId, freeFoodSelected))
                            if mealTypeId == '2':
                                foods_lunch.append(
                                    (j, food_name, price_list, programId, mealTypeId, programDateTime,
                                     foodTypeId, freeFoodSelected))
                            if mealTypeId == '3':
                                foods_dinner.append(
                                    (j, food_name, price_list, programId, mealTypeId, programDateTime,
                                     foodTypeId, freeFoodSelected))
                        else:
                            newfood = Food()
                            newfood.name = re.findall(r'\|(.+)', food_name)[0]
                            newfood.university = user_data.university
                            newfood.save()
                            u = UserPreferableFood()
                            u.user = user_data.user
                            u.food = newfood
                            u.score = 0
                            u.save()

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

            saturdays_date = list()
            date = str(jdatetime.date.today() + jdatetime.timedelta(3))
            date = re.sub(r'\-', '/', date)
            saturdays_date.append(date)
            saturdays_date = str(saturdays_date)

            filter = ReservedTable.objects.filter(user=user_data.user, week_start_date=saturdays_date)
            if not filter:
                reserved = ReservedTable()
                reserved.user = user_data.user
                reserved.week_start_date = saturdays_date
            else:
                reserved = filter[0]

            for item in lunch_data:
                k = 0
                while k < len(lunch_data[item]):
                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].selected'] = 'false'
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
                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].selectedCount'] = 1
                    payload_reserve[f'userWeekReserves[{lunch_data[item][k][0]}].freeFoodSelected'] = \
                        lunch_data[item][k][7]

                k = 0
                while k < len(breakfast_data[item]):
                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].selected'] = 'false'
                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].id'] = ''
                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].programId'] = \
                        breakfast_data[item][k][3]
                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].mealTypeId'] = \
                        breakfast_data[item][k][4]
                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].programDateTime'] = \
                        breakfast_data[item][k][5]
                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].selfId'] = self.self_id
                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].foodTypeId'] = \
                        breakfast_data[item][k][6]
                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].selectedCount'] = 1
                    payload_reserve[f'userWeekReserves[{breakfast_data[item][k][0]}].freeFoodSelected'] = \
                        breakfast_data[item][k][7]

                k = 0
                while k < len(dinner_data[item]):
                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].selected'] = 'false'
                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].id'] = ''
                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].programId'] = \
                        dinner_data[item][k][3]
                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].mealTypeId'] = \
                        dinner_data[item][k][4]
                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].programDateTime'] = \
                        dinner_data[item][k][5]
                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].selfId'] = self.self_id
                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].foodTypeId'] = \
                        dinner_data[item][k][6]
                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].selectedCount'] = 1
                    payload_reserve[f'userWeekReserves[{dinner_data[item][k][0]}].freeFoodSelected'] = \
                        dinner_data[item][k][7]

                for daye in dinner_data:
                    if dinner_data[daye]:
                        for day in chosen_days_lunch:
                            if daye[0] == day and (dinner_data[daye] is not None):
                                food_list = []
                                for food in dinner_data[daye]:
                                    food_list.append((food[0],
                                                      UserPreferableFood.objects.filter(user=user_data.user,
                                                                                        food__name=food[1])[0],
                                                      food[2]))
                                food_list.sort(key=lambda x: x[1].score, reverse=True)
                                prefered_data = food_list
                                if prefered_data:
                                    payload_reserve[
                                        f'userWeekReserves[{prefered_data[0][0]}].selected'] = 'true'

                                    a = int(prefered_data[0][2])
                                    total_price += a

                                    if day == 'شنبه':
                                        reserved.saturday_dinner = prefered_data[0][1].food
                                        reserved.saturday_dinner_self = self.self_name
                                    if day == 'یکشنبه':
                                        reserved.sunday_dinner = prefered_data[0][1].food
                                        reserved.sunday_dinner_self = self.self_name
                                    if day == 'دوشنبه':
                                        reserved.monday_dinner = prefered_data[0][1].food
                                        reserved.monday_dinner_self = self.self_name
                                    if day == 'سه شنبه':
                                        reserved.tuesday_dinner = prefered_data[0][1].food
                                        reserved.tuesday_dinner_self = self.self_name
                                    if day == 'چهارشنبه':
                                        reserved.wednesday_dinner = prefered_data[0][1].food
                                        reserved.wednesday_dinner_self = self.self_name
                                    if day == 'پنجشنبه':
                                        reserved.thursday_dinner = prefered_data[0][1].food
                                        reserved.thursday_dinner_self = self.self_name
                                    if day == 'جمعه':
                                        reserved.friday_dinner = prefered_data[0][1].food
                                        reserved.friday_dinner_self = self.self_name

                for daye in lunch_data:
                    if lunch_data[daye]:
                        for day in chosen_days_lunch:
                            if daye[0] == day and (lunch_data[daye] is not None):
                                food_list = []
                                for food in lunch_data[daye]:
                                    food_list.append((food[0],
                                                      UserPreferableFood.objects.filter(user=user_data.user,
                                                                                        food__name=food[1])[0],
                                                      food[2]))
                                food_list.sort(key=lambda x: x[1].score, reverse=True)
                                prefered_data = food_list
                                if prefered_data:
                                    payload_reserve[
                                        f'userWeekReserves[{prefered_data[0][0]}].selected'] = 'true'
                                    a = int(prefered_data[0][2])
                                    total_price += a

                                    if day == 'شنبه':
                                        reserved.saturday_lunch = prefered_data[0][1].food
                                        reserved.saturday_lunch_self = self.self_name
                                    if day == 'یکشنبه':
                                        reserved.sunday_lunch = prefered_data[0][1].food
                                        reserved.sunday_lunch_self = self.self_name
                                    if day == 'دوشنبه':
                                        reserved.monday_lunch = prefered_data[0][1].food
                                        reserved.monday_lunch_self = self.self_name
                                    if day == 'سه شنبه':
                                        reserved.tuesday_lunch = prefered_data[0][1].food
                                        reserved.tuesday_lunch_self = self.self_name
                                    if day == 'چهارشنبه':
                                        reserved.wednesday_lunch = prefered_data[0][1].food
                                        reserved.wednesday_lunch_self = self.self_name
                                    if day == 'پنجشنبه':
                                        reserved.thursday_lunch = prefered_data[0][1].food
                                        reserved.thursday_lunch_self = self.self_name
                                    if day == 'جمعه':
                                        reserved.friday_lunch = prefered_data[0][1].food
                                        reserved.friday_lunch_self = self.self_name

                for daye in breakfast_data:
                    if breakfast_data[daye]:
                        for day in chosen_days_breakfast:
                            if daye[0] == day and (breakfast_data[daye] is not None):
                                food_list = []
                                for food in breakfast_data[daye]:
                                    food_list.append((food[0],
                                                      UserPreferableFood.objects.filter(user=user_data.user,
                                                                                        food__name=food[1])[0],
                                                      food[2]))
                                food_list.sort(key=lambda x: x[1].score, reverse=True)
                                prefered_data = food_list
                                if prefered_data:
                                    payload_reserve[
                                        f'userWeekReserves[{prefered_data[0][0]}].selected'] = 'true'

                                    a = int(prefered_data[0][2])
                                    total_price += a
                                    if day == 'شنبه':
                                        reserved.saturday_lunch = prefered_data[0][1].food
                                        reserved.saturday_breakfast_self = self.self_name
                                    if day == 'یکشنبه':
                                        reserved.sunday_lunch = prefered_data[0][1].food
                                        reserved.sunday_breakfast_self = self.self_name
                                    if day == 'دوشنبه':
                                        reserved.monday_lunch = prefered_data[0][1].food
                                        reserved.monday_breakfast_self = self.self_name
                                    if day == 'سه شنبه':
                                        reserved.tuesday_lunch = prefered_data[0][1].food
                                        reserved.tuesday_breakfast_self = self.self_name
                                    if day == 'چهارشنبه':
                                        reserved.wednesday_lunch = prefered_data[0][1].food
                                        reserved.wednesday_breakfast_self = self.self_name
                                    if day == 'پنجشنبه':
                                        reserved.thursday_lunch = prefered_data[0][1].food
                                        reserved.thursday_breakfast_self = self.self_name
                                    if day == 'جمعه':
                                        reserved.friday_lunch = prefered_data[0][1].food
                                        reserved.friday_breakfast_self = self.self_name

                    payload_reserve['remainCredit'] = Credit - total_price

            session_requests.post(reserve_get_url, data=payload_reserve)
        reserved.save()
