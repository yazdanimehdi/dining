from django.db import models


class FoodUser(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=11)
    chat_id = models.BigIntegerField(default=0)
    number = models.IntegerField(default=0)

    def __str__(self):
        return self.name
