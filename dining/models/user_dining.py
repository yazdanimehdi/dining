from django.db import models
from django.conf import settings


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

    def __str__(self):
        return str(self.user)


class UserPreferableFood(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    food = models.ForeignKey(to='dining.Food', on_delete=models.CASCADE)
    score = models.SmallIntegerField(default=0)

    def __str__(self):
        return str(self.user)


class UserServicesUniversities(models.Model):
    university = models.ForeignKey(to='dining.University', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    served_breakfast_self_id = models.CharField(max_length=10)
    served_breakfast_self_name = models.CharField(max_length=100)
    served_lunch_self_id = models.CharField(max_length=10)
    served_lunch_self_name = models.CharField(max_length=100)
    served_dinner_self_id = models.CharField(max_length=10)
    served_dinner_self_name = models.CharField(max_length=100)









#
# UserPreferableFood.objects.filter(user__username='Ali', food__university__id=1, food_name__in=[]).order_by('-score')

