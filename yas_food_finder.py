import pickle
import re
import shutil

import cv2
import jdatetime
import numpy as np
import requests
from keras.models import load_model
from lxml import html

from dining.models import University, Food
from helpers import resize_to_fit

login_url = 'http://meal.khu.ac.ir'
captcha_url = 'http://meal.khu.ac.ir/GenerateCaptcha.ashx'
reserve_get_url = 'http://meal.khu.ac.ir/Reserve.aspx'
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

username = '68559'
password = '1373'
date = re.sub(r'-', '', str(jdatetime.date.today() + jdatetime.timedelta(1)))[2:]
kinds = [0, 1, 2]
days = [0, 1, 2, 3, 4, 5, 6]
payload = {
    'txtusername': '68559',
    'txtpassword': '1373',
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

# # Finding Selfs
# self_id = re.findall(r'<option value=\"(.+?)\"', result.text)
# self_names = re.findall(r'<option value=\".*\">(.+)</option>', result.text)
# self_dict = dict()
# i = 0
# for item in self_names:
#     self_dict[item] = self_id[i]
#     i += 1
#
# for self in self_id:
i = 0

while i < 64:
    date = re.sub(r'-', '', str(jdatetime.date.today() + jdatetime.timedelta(1) - jdatetime.timedelta(7 * i)))[2:]
    # Extracting Foods
    breakfast_data = dict()
    lunch_data = dict()
    dinner_data = dict()
    for day in days:
        for kind in kinds:
            meal_url = f'http://meal.khu.ac.ir/SelectGhaza.aspx?date={date}&dow={day}&kind={kind}&sel=False&selg=True&week=1&personeli={username}'
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
                if Food.objects.filter(university__name='دانشگاه خوارزمی کرج'):
                    for db_food in Food.objects.filter(university__name='دانشگاه خوارزمی کرج'):
                        if set(db_food.name.split(' ')).issubset(food[2].split(' ')):
                            flag = True
                        elif db_food.name in food[2]:
                            flag = True
                        elif '+' in food[2]:
                            if db_food.name in food[2].split('+')[0]:
                                flag = True
                            elif db_food.name in food[2].split('+')[1]:
                                flag = True

                    if not flag:
                        uni = University.objects.get(name='دانشگاه خوارزمی کرج')
                        newfood = Food()
                        newfood.name = food[2].strip()
                        newfood.university = uni
                        newfood.save()
                else:
                    uni = University.objects.get(name='دانشگاه خوارزمی کرج')
                    newfood = Food()
                    newfood.name = food[2].strip()
                    newfood.university = uni
                    newfood.save()
    i += 1
