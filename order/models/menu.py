from django.db import models


class RestaurantMenu(models.Model):
    name = models.CharField(max_length=50)
    restaurant = models.ForeignKey(to='order.Restaurant', on_delete=models.CASCADE)
    food_type = models.CharField(max_length=10, default='main')
    is_active = models.BooleanField(default=True)
    price = models.FloatField()

    def __str__(self):
        return self.name
