from django.db import models


class University(models.Model):
    name = models.CharField(max_length=100)
    tag = models.CharField(max_length=100, default='-')
    login_url = models.CharField(max_length=200)
    simple_url = models.CharField(max_length=100, default='0')
    reserve_table = models.CharField(max_length=200, default='0')
    reserve_url = models.CharField(max_length=200, default='0')
    url_next_week = models.CharField(max_length=200, default='0')
    reserved_table = models.CharField(max_length=200, default='0')
    captcha_url = models.CharField(max_length=400, default='-')
    csrf_name = models.CharField(max_length=100)
    form_username = models.CharField(max_length=100)
    form_password = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Food(models.Model):
    university = models.ForeignKey(to='dining.University', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.university.name + '-----' + self.name
