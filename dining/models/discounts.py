from django.db import models


class Merchants(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=1000, default='')


class MerchantUser(models.Model):
    user = models.ForeignKey(to='dining.CustomUser', on_delete=models.CASCADE)
    merchant = models.ForeignKey(to='dining.Merchants', on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    active = models.BooleanField(default=True)
