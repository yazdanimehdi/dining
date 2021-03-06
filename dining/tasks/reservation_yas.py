import pickle
import re
import shutil

import cv2
import imgkit
import jdatetime
import numpy as np
import pandas as pd
import requests
import telegram
from celery import task
from lxml import html

from helpers import resize_to_fit


@task
def reservation_yas():
    from keras.models import load_model
    from dining.models import UserDiningData, ReservedTable, UserSelfs, UserPreferableFood, SamadPrefrredDays, Food
    for user_data in UserDiningData.objects.filter(university__tag='yas'):
        if user_data.user.is_paid:
            try:
                login_url = user_data.university.login_url
                captcha_url = user_data.university.captcha_url
                reserve_get_url = user_data.university.reserve_url
                i = 830

                session_requests = requests.session()
                result = session_requests.get(login_url)
                captcha = session_requests.get(captcha_url, stream=True)
                with open('img.png', 'wb') as out_file:
                    shutil.copyfileobj(captcha.raw, out_file)
                image_file = 'img.png'

                def inverte(imagem, name):
                    imagem = (255 - imagem)
                    cv2.imwrite(name, imagem)

                imagem = cv2.imread(image_file)
                inverte(imagem, '2.png')
                MODEL_FILENAME = "captcha_model.hdf5"
                MODEL_LABELS_FILENAME = "model_labels.dat"

                with open(MODEL_LABELS_FILENAME, "rb") as f:
                    lb = pickle.load(f)

                image_file = '2.png'
                model = load_model(MODEL_FILENAME)

                image = cv2.imread(image_file)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                image = cv2.copyMakeBorder(image, 20, 20, 20, 20, cv2.BORDER_REPLICATE)

                thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

                contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                letter_image_regions = []

                for contour in contours:
                    (x, y, w, h) = cv2.boundingRect(contour)
                    if w / h > 1.25:
                        half_width = int(w / 2)
                        letter_image_regions.append((x, y, half_width, h))
                        letter_image_regions.append((x + half_width, y, half_width, h))
                    else:
                        letter_image_regions.append((x, y, w, h))

                letter_image_regions = sorted(letter_image_regions, key=lambda x: x[0])

                output = cv2.merge([image] * 3)
                predictions = []

                for letter_bounding_box in letter_image_regions:
                    x, y, w, h = letter_bounding_box
                    letter_image = image[y - 2:y + h + 2, x - 2:x + w + 2]

                    letter_image = resize_to_fit(letter_image, 20, 20)

                    letter_image = np.expand_dims(letter_image, axis=2)
                    letter_image = np.expand_dims(letter_image, axis=0)

                    prediction = model.predict(letter_image)

                    letter = lb.inverse_transform(prediction)[0]
                    predictions.append(letter)

                captcha_text = "".join(predictions)

                tree = html.fromstring(result.text)
                VIEWSTATE = list(set(tree.xpath("//input[@name='__VIEWSTATE']/@value")))[0]
                VIEWSTATEGENERATOR = list(set(tree.xpath("//input[@name='__VIEWSTATEGENERATOR']/@value")))[0]
                VIEWSTATEENCRYPTED = list(set(tree.xpath("//input[@name='__VIEWSTATEENCRYPTED']/@value")))[0]
                EVENTVALIDATION = list(set(tree.xpath("//input[@name='__EVENTVALIDATION']/@value")))[0]

                username = user_data.dining_username
                password = user_data.dining_password
                date = re.sub(r'-', '', str(jdatetime.date.today() + jdatetime.timedelta(3)))[2:]
                kinds = [0, 1, 2]
                days = [0, 1, 2, 3, 4, 5, 6]
                payload = {
                    'txtusername': username,
                    'txtpassword': password,
                    'txtCaptchaText': captcha_text,
                    '__VIEWSTATE': VIEWSTATE,
                    '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
                    '__VIEWSTATEENCRYPTED': VIEWSTATEENCRYPTED,
                    '__EVENTVALIDATION': EVENTVALIDATION,
                    '__LASTFOCUS': '',
                    '__EVENTTARGET': '',
                    '__EVENTARGUMENT': '',
                    'btnlogin': 'ورود',

                }

                result = session_requests.post(login_url, data=payload, headers=dict(referer=login_url))
                result = session_requests.get(reserve_get_url)

                for self in UserSelfs.objects.filter(user=user_data.user, is_active=True):
                    # Extracting Foods
                    breakfast_data = dict()
                    lunch_data = dict()
                    dinner_data = dict()
                    for day in days:
                        for kind in kinds:
                            meal_url = f'{login_url}/SelectGhaza.aspx?date={date}&dow={day}&kind={kind}&sel=False&selg=True&week=1&personeli={username}'
                            result = session_requests.get(meal_url)
                            regex_find = re.findall(r'javascript:SelectGhaza\((.+)\)', result.text)
                            foods = []
                            for item in regex_find:
                                food = []
                                particles = item.split(',')
                                for particle in particles:
                                    particle = particle.strip('"')
                                    food.append(particle)
                                flag = False
                                for db_food in Food.objects.filter(university=user_data.university):
                                    if set(db_food.name.split(' ')).issubset(food[2].split(' ')):
                                        flag = True
                                        food[2] = db_food.name
                                    elif db_food.name in food[2]:
                                        flag = True
                                        food[2] = db_food.name
                                    elif '+' in food[2]:
                                        if db_food.name in food[2].split('+')[0]:
                                            flag = True
                                            food[2] = db_food.name
                                        elif db_food.name in food[2].split('+')[1]:
                                            flag = True
                                            food[2] = db_food.name
                                if not flag:
                                    uni = user_data.university
                                    newfood = Food()
                                    newfood.name = food[2].strip()
                                    newfood.university = uni
                                foods.append(food)
                            if kind == 0:
                                breakfast_data[day] = foods
                            elif kind == 1:
                                lunch_data[day] = foods
                            elif kind == 2:
                                dinner_data[day] = foods

                    result = session_requests.get(reserve_get_url)
                    tree = html.fromstring(result.text)
                    VIEWSTATE = list(set(tree.xpath("//input[@name='__VIEWSTATE']/@value")))[0]
                    VIEWSTATEGENERATOR = list(set(tree.xpath("//input[@name='__VIEWSTATEGENERATOR']/@value")))[0]
                    VIEWSTATEENCRYPTED = list(set(tree.xpath("//input[@name='__VIEWSTATEENCRYPTED']/@value")))[0]
                    EVENTVALIDATION = list(set(tree.xpath("//input[@name='__EVENTVALIDATION']/@value")))[0]

                    payload_next_week = {
                        '__VIEWSTATE': VIEWSTATE,
                        '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
                        '__VIEWSTATEENCRYPTED': VIEWSTATEENCRYPTED,
                        '__EVENTVALIDATION': EVENTVALIDATION,
                        '__EVENTTARGET': 'btnnextweek1',
                        '__EVENTARGUMENT': '',

                    }
                    result = session_requests.post(reserve_get_url, payload_next_week)
                    tree = html.fromstring(result.text)
                    VIEWSTATE = list(set(tree.xpath("//input[@name='__VIEWSTATE']/@value")))[0]
                    VIEWSTATEGENERATOR = list(set(tree.xpath("//input[@name='__VIEWSTATEGENERATOR']/@value")))[0]
                    VIEWSTATEENCRYPTED = list(set(tree.xpath("//input[@name='__VIEWSTATEENCRYPTED']/@value")))[0]
                    EVENTVALIDATION = list(set(tree.xpath("//input[@name='__EVENTVALIDATION']/@value")))[0]

                    payload_reserve = {
                        '__VIEWSTATE': VIEWSTATE,
                        '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
                        '__VIEWSTATEENCRYPTED': VIEWSTATEENCRYPTED,
                        '__EVENTVALIDATION': EVENTVALIDATION,
                        '__EVENTTARGET': '',
                        '__EVENTARGUMENT': '',
                        'RD_Self': self.self_id,
                        'Self': self.self_id,
                        'btn_saveKharid': 'تائید'
                    }

                    pdays = SamadPrefrredDays.objects.get(user=user_data.user, active_self=self)

                    chosen_days_breakfast = []
                    if pdays.reserve_friday_breakfast:
                        chosen_days_breakfast.append(7)
                    if pdays.reserve_saturday_breakfast:
                        chosen_days_breakfast.append(1)
                    if pdays.reserve_sunday_breakfast:
                        chosen_days_breakfast.append(2)
                    if pdays.reserve_monday_breakfast:
                        chosen_days_breakfast.append(3)
                    if pdays.reserve_tuesday_breakfast:
                        chosen_days_breakfast.append(4)
                    if pdays.reserve_wednesday_breakfast:
                        chosen_days_breakfast.append(5)
                    if pdays.reserve_thursday_breakfast:
                        chosen_days_breakfast.append(6)

                    chosen_days_lunch = []

                    if pdays.reserve_friday_lunch:
                        chosen_days_lunch.append(7)
                    if pdays.reserve_saturday_lunch:
                        chosen_days_lunch.append(1)
                    if pdays.reserve_sunday_lunch:
                        chosen_days_lunch.append(2)
                    if pdays.reserve_monday_lunch:
                        chosen_days_lunch.append(3)
                    if pdays.reserve_tuesday_lunch:
                        chosen_days_lunch.append(4)
                    if pdays.reserve_wednesday_lunch:
                        chosen_days_lunch.append(5)
                    if pdays.reserve_thursday_lunch:
                        chosen_days_lunch.append(6)

                    chosen_days_dinner = []

                    if pdays.reserve_friday_dinner:
                        chosen_days_dinner.append(7)
                    if pdays.reserve_saturday_dinner:
                        chosen_days_dinner.append(1)
                    if pdays.reserve_sunday_dinner:
                        chosen_days_dinner.append(2)
                    if pdays.reserve_monday_dinner:
                        chosen_days_dinner.append(3)
                    if pdays.reserve_tuesday_dinner:
                        chosen_days_dinner.append(4)
                    if pdays.reserve_wednesday_lunch:
                        chosen_days_dinner.append(5)
                    if pdays.reserve_thursday_dinner:
                        chosen_days_dinner.append(6)

                    # finding values
                    txtn_numGhaza = list()
                    GhazaN = list()
                    EditN = list()
                    Hid = list()
                    HidN = list()

                    txtc_numGhaza = list()
                    GhazaC = list()
                    EditC = list()
                    HidC = list()
                    HidCN = list()

                    txts_numGhaza = list()
                    GhazaS = list()
                    EditS = list()
                    HidS = list()
                    HidSN = list()
                    days = [1, 2, 3, 4, 5, 6, 7]
                    for i in days:
                        txtn_numGhaza.append(list(set(tree.xpath(f"//input[@name='txtn_numGhaza{i}']/@value")))[0])
                        GhazaN.append(list(set(tree.xpath(f"//input[@name='GhazaN{i}']/@value")))[0])
                        EditN.append(list(set(tree.xpath(f"//input[@name='EditN{i}']/@value")))[0])
                        Hid.append(list(set(tree.xpath(f"//input[@name='Hid{i}']/@value")))[0])
                        HidN.append(list(set(tree.xpath(f"//input[@name='HidN{i}']/@value")))[0])

                        txtc_numGhaza.append(list(set(tree.xpath(f"//input[@name='txtc_numGhaza{i}']/@value")))[0])
                        GhazaC.append(list(set(tree.xpath(f"//input[@name='GhazaC{i}']/@value")))[0])
                        EditC.append(list(set(tree.xpath(f"//input[@name='EditC{i}']/@value")))[0])
                        HidC.append(list(set(tree.xpath(f"//input[@name='HidC{i}']/@value")))[0])
                        HidCN.append(list(set(tree.xpath(f"//input[@name='HidCN{i}']/@value")))[0])

                        txts_numGhaza.append(list(set(tree.xpath(f"//input[@name='txts_numGhaza{i}']/@value")))[0])
                        GhazaS.append(list(set(tree.xpath(f"//input[@name='GhazaS{i}']/@value")))[0])
                        EditS.append(list(set(tree.xpath(f"//input[@name='EditS{i}']/@value")))[0])
                        HidS.append(list(set(tree.xpath(f"//input[@name='HidS{i}']/@value")))[0])
                        HidSN.append(list(set(tree.xpath(f"//input[@name='HidSN{i}']/@value")))[0])

                    for i in days:
                        # lunch payload
                        payload_reserve[f'txtn_numGhaza{i}'] = txtn_numGhaza[i - 1]
                        payload_reserve[f'GhazaN{i}'] = GhazaN[i - 1]
                        payload_reserve[f'EditN{i}'] = EditN[i - 1]
                        payload_reserve[f'Hid{i}'] = Hid[i - 1]
                        payload_reserve[f'HidN{i}'] = HidN[i - 1]
                        # breakfast payload
                        payload_reserve[f'txtc_numGhaza{i}'] = txtc_numGhaza[i - 1]
                        payload_reserve[f'EditC{i}'] = EditC[i - 1]
                        payload_reserve[f'GhazaC{i}'] = GhazaC[i - 1]
                        payload_reserve[f'HidC{i}'] = HidC[i - 1]
                        payload_reserve[f'HidCN{i}'] = HidCN[i - 1]

                        # dinner payload
                        payload_reserve[f'txts_numGhaza{i}'] = txts_numGhaza[i - 1]
                        payload_reserve[f'EditS{i}'] = EditS[i - 1]
                        payload_reserve[f'GhazaS{i}'] = GhazaS[i - 1]
                        payload_reserve[f'HidS{i}'] = HidS[i - 1]
                        payload_reserve[f'HidSN{i}'] = HidSN[i - 1]

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

                    for day in chosen_days_breakfast:
                        if breakfast_data[day - 1]:
                            food_list = []
                            for food in breakfast_data[day - 1]:
                                food_list.append((food, UserPreferableFood.objects.filter(user=user_data.user,
                                                                                          food__name=food[2])[0]))
                            food_list.sort(key=lambda x: x[1].score, reverse=True)
                            prefered_data = food_list
                            payload_reserve[f'txtc_numGhaza{day}'] = 1
                            payload_reserve[f'EditC{day}'] = self.self_id
                            payload_reserve[f'GhazaC{day}'] = prefered_data[0][0][0]
                            payload_reserve[f'HidC{day}'] = prefered_data[0][0][4]
                            payload_reserve[f'HidCN{day}'] = prefered_data[0][0][0]

                            if day == 1:
                                reserved.saturday_lunch = prefered_data[0][1].food.name
                                reserved.saturday_breakfast_self = self.self_name
                            if day == 2:
                                reserved.sunday_lunch = prefered_data[0][1].food.name
                                reserved.sunday_breakfast_self = self.self_name
                            if day == 3:
                                reserved.monday_lunch = prefered_data[0][1].food.name
                                reserved.monday_breakfast_self = self.self_name
                            if day == 4:
                                reserved.tuesday_lunch = prefered_data[0][1].food.name
                                reserved.tuesday_breakfast_self = self.self_name
                            if day == 5:
                                reserved.wednesday_lunch = prefered_data[0][1].food.name
                                reserved.wednesday_breakfast_self = self.self_name
                            if day == 6:
                                reserved.thursday_lunch = prefered_data[0][1].food.name
                                reserved.thursday_breakfast_self = self.self_name
                            if day == 7:
                                reserved.friday_lunch = prefered_data[0][1].food.name
                                reserved.friday_breakfast_self = self.self_name

                    for day in chosen_days_lunch:
                        if lunch_data[day - 1]:
                            food_list = []
                            for food in lunch_data[day - 1]:
                                food_list.append((food, UserPreferableFood.objects.filter(user=user_data.user,
                                                                                          food__name=food[2])[0]))
                            food_list.sort(key=lambda x: x[1].score, reverse=True)
                            prefered_data = food_list
                            payload_reserve[f'txtn_numGhaza{day}'] = 1
                            payload_reserve[f'GhazaN{day}'] = prefered_data[0][0][0]
                            payload_reserve[f'EditN{day}'] = self.self_id
                            payload_reserve[f'Hid{day}'] = prefered_data[0][0][4]
                            payload_reserve[f'HidN{day}'] = prefered_data[0][0][0]

                            if day == 1:
                                reserved.saturday_lunch = prefered_data[0][1].food.name
                                reserved.saturday_lunch_self = self.self_name
                            if day == 2:
                                reserved.sunday_lunch = prefered_data[0][1].food.name
                                reserved.sunday_lunch_self = self.self_name
                            if day == 3:
                                reserved.monday_lunch = prefered_data[0][1].food.name
                                reserved.monday_lunch_self = self.self_name
                            if day == 4:
                                reserved.tuesday_lunch = prefered_data[0][1].food.name
                                reserved.tuesday_lunch_self = self.self_name
                            if day == 5:
                                reserved.wednesday_lunch = prefered_data[0][1].food.name
                                reserved.wednesday_lunch_self = self.self_name
                            if day == 6:
                                reserved.thursday_lunch = prefered_data[0][1].food.name
                                reserved.thursday_lunch_self = self.self_name
                            if day == 7:
                                reserved.friday_lunch = prefered_data[0][1].food.name
                                reserved.friday_lunch_self = self.self_name

                    for day in chosen_days_dinner:
                        if dinner_data[day - 1]:
                            food_list = []
                            for food in dinner_data[day - 1]:
                                food_list.append((food, UserPreferableFood.objects.filter(user=user_data.user,
                                                                                          food__name=food[2])[0]))
                            food_list.sort(key=lambda x: x[1].score, reverse=True)
                            prefered_data = food_list
                            payload_reserve[f'txts_numGhaza{day}'] = 1
                            payload_reserve[f'GhazaS{day}'] = prefered_data[0][0][0]
                            payload_reserve[f'EditS{day}'] = self.self_id
                            payload_reserve[f'HidS{day}'] = prefered_data[0][0][4]
                            payload_reserve[f'HidSN{day}'] = prefered_data[0][0][0]

                            if day == 1:
                                reserved.saturday_dinner = prefered_data[0][1].food.name
                                reserved.saturday_dinner_self = self.self_name
                            if day == 2:
                                reserved.sunday_dinner = prefered_data[0][1].food.name
                                reserved.sunday_dinner_self = self.self_name
                            if day == 3:
                                reserved.monday_dinner = prefered_data[0][1].food.name
                                reserved.monday_dinner_self = self.self_name
                            if day == 4:
                                reserved.tuesday_dinner = prefered_data[0][1].food.name
                                reserved.tuesday_dinner_self = self.self_name
                            if day == 5:
                                reserved.wednesday_dinner = prefered_data[0][1].food.name
                                reserved.wednesday_dinner_self = self.self_name
                            if day == 6:
                                reserved.thursday_dinner = prefered_data[0][1].food.name
                                reserved.thursday_dinner_self = self.self_name
                            if day == 7:
                                reserved.friday_dinner = prefered_data[0][1].food.name
                                reserved.friday_dinner_self = self.self_name
                    result = session_requests.post(reserve_get_url, data=payload_reserve)
                    error = re.findall(r'message_error.+\">(.+)<\/font>', result.text)

                    credit = float(re.sub(r',', '', re.findall(r'id="lbEtebar">(.+)</span>', result.text)[0]))
                    reserved.credit = credit
                    reserved.save()

                    if user_data.user.chat_id != 0:
                        data = {'صبحانه': [reserved.saturday_breakfast, reserved.sunday_breakfast,
                                           reserved.monday_breakfast,
                                           reserved.tuesday_breakfast, reserved.wednesday_breakfast,
                                           reserved.thursday_breakfast,
                                           reserved.friday_breakfast],
                                'ناهار': [reserved.saturday_lunch, reserved.sunday_lunch, reserved.monday_lunch,
                                          reserved.tuesday_lunch, reserved.wednesday_lunch, reserved.thursday_lunch,
                                          reserved.friday_lunch],
                                'شام': [reserved.saturday_dinner, reserved.sunday_dinner, reserved.monday_dinner,
                                        reserved.tuesday_dinner, reserved.wednesday_dinner, reserved.thursday_dinner,
                                        reserved.friday_dinner]}
                        df = pd.DataFrame(data,
                                          index=['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه'])

                        css = """
                        <!DOCTYPE html>
                        <head>
                            <meta charset="UTF-8">
                        </head>
                        <style type=\"text/css\">
                        table {
                        color: #333;
                        font-family: Helvetica, Arial, sans-serif;
                        width: 640px;
                        border-collapse:
                        collapse; 
                        border-spacing: 0;
                        }
                        td, th {
                        border: 1px solid transparent; /* No more visible border */
                        height: 30px;
                        }
                        th {
                        background: #DFDFDF; /* Darken header a bit */
                        font-weight: bold;
                        }
                        td {
                        background: #FAFAFA;
                        text-align: center;
                        }
                        table tr:nth-child(odd) td{
                        background-color: white;
                        }
                        </style>
                        """
                        with open('html.html', 'w') as f:
                            f.write('')
                        text_file = open("html.html", "a")
                        text_file.write(css)
                        text_file.write(df.to_html())
                        text_file.close()
                        imgkitoptions = {"format": "png"}
                        imgkit.from_file("html.html", 'reserve_img.png', options=imgkitoptions)

                        def send_photo(path, chat_id, token):
                            bot = telegram.Bot(token=token)
                            bot.send_photo(chat_id=chat_id, photo=open(path, 'rb'))

                        def send(msg, chat_id, token):
                            bot = telegram.Bot(token=token)
                            bot.send_message(chat_id=chat_id, text=msg)

                        bot_token = '610448118:AAFVPBXMKPzqAiOJ9-zhusKrOloCiJuEwi8'
                        if not error or error[0] == '':
                            message = "سلام\nامروز چهارشنبه‌س و غذاهاتو برات رزرو کردم\nغذاهایی که رزرو کردم ایناست\n"
                            send(message, str(user_data.user.chat_id), bot_token)
                            send_photo(path='reserve_img.png', chat_id=str(user_data.user.chat_id), token=bot_token)
                        else:
                            message = "سلام توی رزرو غذات به مشکل زیر خوردیم"
                            send(message, str(user_data.user.chat_id), bot_token)
                            message = error[0]
                            send(message, str(user_data.user.chat_id), bot_token)
                            message = "سلام\nامروز چهارشنبه‌س و غذاهاتو برات رزرو کردم\nغذاهایی که رزرو کردم ایناست\n"
                            send(message, str(user_data.user.chat_id), bot_token)
                            send_photo(path='reserve_img.png', chat_id=str(user_data.user.chat_id), token=bot_token)
            except Exception as e:
                print(e)
