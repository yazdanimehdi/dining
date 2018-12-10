import re

import requests
from django.conf import settings
from django.db import models
from lxml import html


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
        login_url = self.university.login_url
        session_requests = requests.session()
        result = session_requests.get(login_url)
        csrf = self.university.csrf_name
        tree = html.fromstring(result.text)
        authenticity_token = list(set(tree.xpath(f"//input[@name='{csrf}']/@value")))[0]
        payload = {
            self.university.form_username: self.dining_username,
            self.university.form_password: self.dining_password,
            self.university.csrf_name: authenticity_token,
        }
        result = session_requests.post(login_url, data=payload, headers=dict(referer=login_url))
        result = session_requests.get(self.university.reserve_url)
        self_id = re.findall(r'<option value=\"(.+?)\"', result.text)
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








#
# UserPreferableFood.objects.filter(user__username='Ali', food__university__id=1, food_name__in=[]).order_by('-score')

