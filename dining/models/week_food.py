from django.db import models


class Dicty(models.Model):
    name = models.CharField(max_length=50)


class Key(models.Model):
    container = models.ForeignKey(to='dining.Dicty', on_delete=models.CASCADE)
    key = models.CharField(max_length=240)


class Val(models.Model):
    container = models.ForeignKey(to='dining.Dicty', on_delete=models.CASCADE)
    key = models.ForeignKey(to='dining.Key', on_delete=models.CASCADE)
    name = models.CharField(max_length=240)
    food_id = models.CharField(max_length=240)
