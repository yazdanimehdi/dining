from django.db import models


class University(models.Model):
    name = models.CharField(max_length=100)
    login_url = models.CharField(max_length=200)
    reserve_table = models.CharField(max_length=200)
    reserve_url = models.CharField(max_length=200)
    reserved_table = models.CharField(max_length=200)
    csrf_name = models.CharField(max_length=100)
    form_username = models.CharField(max_length=100)
    form_password = models.CharField(max_length=100)


class Food(models.Model):
    university = models.ForeignKey(to='dining.University', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    food_id = models.CharField(max_length=20)




