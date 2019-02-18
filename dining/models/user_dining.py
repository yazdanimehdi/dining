import pickle
import re
import shutil

import cv2
import numpy as np
import requests
from django.conf import settings
from django.db import models
from lxml import html

from helpers import resize_to_fit


def get_captcha_text(img):
    from keras.models import load_model

    def inverte(imagem, name):
        imagem = (255 - imagem)
        cv2.imwrite(name, imagem)

    imagem = cv2.imread(img)
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
    return captcha_text


class UserDiningData(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    university = models.ForeignKey(to='dining.University', on_delete=models.CASCADE)
    dining_username = models.CharField(max_length=25)
    dining_password = models.CharField(max_length=25)
    # Breakfast data
    reserve_sunday_breakfast = models.BooleanField(default=False)
    reserve_monday_breakfast = models.BooleanField(default=False)
    reserve_tuesday_breakfast = models.BooleanField(default=False)
    reserve_wednesday_breakfast = models.BooleanField(default=False)
    reserve_thursday_breakfast = models.BooleanField(default=False)
    reserve_friday_breakfast = models.BooleanField(default=False)
    reserve_saturday_breakfast = models.BooleanField(default=False)
    # lunch data
    reserve_sunday_lunch = models.BooleanField(default=False)
    reserve_monday_lunch = models.BooleanField(default=False)
    reserve_tuesday_lunch = models.BooleanField(default=False)
    reserve_wednesday_lunch = models.BooleanField(default=False)
    reserve_thursday_lunch = models.BooleanField(default=False)
    reserve_friday_lunch = models.BooleanField(default=False)
    reserve_saturday_lunch = models.BooleanField(default=False)
    # dinner data
    reserve_sunday_dinner = models.BooleanField(default=False)
    reserve_monday_dinner = models.BooleanField(default=False)
    reserve_tuesday_dinner = models.BooleanField(default=False)
    reserve_wednesday_dinner = models.BooleanField(default=False)
    reserve_thursday_dinner = models.BooleanField(default=False)
    reserve_friday_dinner = models.BooleanField(default=False)
    reserve_saturday_dinner = models.BooleanField(default=False)

    def test_account(self):
        if self.university.tag == 'yas':

            login_url = self.university.login_url
            url = self.university.reserve_table
            captcha_url = self.university.captcha_url
            session_requests = requests.session()
            result = session_requests.get(login_url)
            captcha = session_requests.get(captcha_url, stream=True)

            with open('img.png', 'wb') as out_file:
                shutil.copyfileobj(captcha.raw, out_file)
            image_file = 'img.png'
            tree = html.fromstring(result.text)
            VIEWSTATE = list(set(tree.xpath("//input[@name='__VIEWSTATE']/@value")))[0]
            VIEWSTATEGENERATOR = list(set(tree.xpath("//input[@name='__VIEWSTATEGENERATOR']/@value")))[0]
            VIEWSTATEENCRYPTED = list(set(tree.xpath("//input[@name='__VIEWSTATEENCRYPTED']/@value")))[0]
            EVENTVALIDATION = list(set(tree.xpath("//input[@name='__EVENTVALIDATION']/@value")))[0]

            username = self.dining_username
            password = self.dining_password

            payload = {
                'txtusername': username,
                'txtpassword': password,
                'txtCaptchaText': get_captcha_text(image_file),
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
            result = session_requests.get(url)
            self_id = re.findall(r'<option value=\"(.+?)\"', result.text)
            self_names = re.findall(r'<option value=\".*\">(.+)</option>', result.text)
            self_id_selected = re.findall(r'<option selected=\"selected\" value=\"(.+?)\"', result.text)
            self_name_selected = re.findall(r'<option selected=\"selected\" value=\".*\">(.+)</option>', result.text)
            self_dict = dict()
            i = 0
            for item in self_names:
                self_dict[item] = self_id[i]
                i += 1
            self_dict[self_name_selected[0]] = self_id_selected[0]

            return self_dict

        else:
            login_url = self.university.login_url
            url = self.university.reserve_table
            session_requests = requests.session()
            if self.university.name == 'دانشگاه تهران':
                login_url = 'https://auth4.ut.ac.ir:8443/cas/login?service=https://dining1.ut.ac.ir/login/cas'
                reserve_get_url = 'https://dining1.ut.ac.ir/nurture/user/multi/reserve/reserve.rose'
                result = session_requests.get(login_url, verify=False)
                tree = html.fromstring(result.text)
                authenticity_token_execution = list(set(tree.xpath("//input[@name='execution']/@value")))[0]
                authenticity_token_lt = list(set(tree.xpath("//input[@name='lt']/@value")))[0]

                payload = {
                    'username': self.dining_username,
                    'password': self.dining_password,
                    'lt': authenticity_token_lt,
                    'execution': authenticity_token_execution,
                    '_eventId': 'submit'

                }
                result = session_requests.post(login_url, data=payload, headers=dict(referer=login_url), verify=False)
                tree = html.fromstring(result.text)
                result = session_requests.get(reserve_get_url, headers=dict(referer=url), verify=False)
                if result.status_code == 403:
                    print(list(set(tree.xpath("//*[@id=\"cas_username\"]/option[2]/@value"))))
                    link = list(set(tree.xpath("//*[@id=\"cas_username\"]/option[2]/@value")))[0]
                    result = session_requests.get('https://dining1.ut.ac.ir' + link, verify=False)
                result = session_requests.get(reserve_get_url, headers=dict(referer=url), verify=False)
            else:
                result = session_requests.get(login_url)
                tree = html.fromstring(result.text)
                authenticity_token = list(set(tree.xpath("//input[@name='_csrf']/@value")))[0]
                payload = {
                    self.university.form_username: self.dining_username,
                    self.university.form_password: self.dining_password,
                    self.university.csrf_name: authenticity_token,
                }
                if self.university.name == 'دانشگاه صنعتی امیرکبیر' or self.university.name == 'دانشگاه شهید بهشتی':
                    payload['login'] = 'ورود'
                result = session_requests.post(login_url, data=payload, headers=dict(referer=login_url))
                result = session_requests.get(url, headers=dict(referer=url))
            self_id = re.findall(r'<option value=\"(\d+?)\"', result.text)
            self_names = re.findall(r'<option value=\".*\">(.+)</option>', result.text)
            self_dict = dict()
            i = 0
            for item in self_names:
                self_dict[item] = self_id[i]
                i += 1
            return self_dict

    def __str__(self):
        return str(self.user)


class UserPreferableFood(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    food = models.ForeignKey(to='dining.Food', on_delete=models.CASCADE)
    score = models.SmallIntegerField(default=0)

    def __str__(self):
        return str(self.user)


class UserSelfs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    self_name = models.CharField(max_length=100)
    self_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)


class SamadPrefrredDays(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    active_self = models.ForeignKey(to='dining.UserSelfs', on_delete=models.CASCADE)
    # Breakfast data
    reserve_sunday_breakfast = models.BooleanField(default=False)
    reserve_monday_breakfast = models.BooleanField(default=False)
    reserve_tuesday_breakfast = models.BooleanField(default=False)
    reserve_wednesday_breakfast = models.BooleanField(default=False)
    reserve_thursday_breakfast = models.BooleanField(default=False)
    reserve_friday_breakfast = models.BooleanField(default=False)
    reserve_saturday_breakfast = models.BooleanField(default=False)
    # lunch data
    reserve_sunday_lunch = models.BooleanField(default=False)
    reserve_monday_lunch = models.BooleanField(default=False)
    reserve_tuesday_lunch = models.BooleanField(default=False)
    reserve_wednesday_lunch = models.BooleanField(default=False)
    reserve_thursday_lunch = models.BooleanField(default=False)
    reserve_friday_lunch = models.BooleanField(default=False)
    reserve_saturday_lunch = models.BooleanField(default=False)
    # dinner data
    reserve_sunday_dinner = models.BooleanField(default=False)
    reserve_monday_dinner = models.BooleanField(default=False)
    reserve_tuesday_dinner = models.BooleanField(default=False)
    reserve_wednesday_dinner = models.BooleanField(default=False)
    reserve_thursday_dinner = models.BooleanField(default=False)
    reserve_friday_dinner = models.BooleanField(default=False)
    reserve_saturday_dinner = models.BooleanField(default=False)
