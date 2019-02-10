from django.db import models


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=11)
    chat_id = models.BigIntegerField(default=0)

    def __str__(self):
        return self.name


class RestaurantUniversityCoverage(models.Model):
    university = models.ForeignKey(to='dining.University', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(to='order.Restaurant', on_delete=models.CASCADE)
