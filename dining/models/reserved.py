from django.db import models


class ReservedTable(models.Model):
    user = models.ForeignKey(to='dining.CustomUser', on_delete=models.CASCADE)

    week_start_date = models.CharField(max_length=100, default='-')

    monday_breakfast = models.CharField(max_length=100, default='-')
    tuesday_breakfast = models.CharField(max_length=100, default='-')
    wednesday_breakfast = models.CharField(max_length=100, default='-')
    thursday_breakfast = models.CharField(max_length=100, default='-')
    friday_breakfast = models.CharField(max_length=100, default='-')
    saturday_breakfast = models.CharField(max_length=100, default='-')
    sunday_breakfast = models.CharField(max_length=100, default='-')

    monday_lunch = models.CharField(max_length=100, default='-')
    tuesday_lunch = models.CharField(max_length=100, default='-')
    wednesday_lunch = models.CharField(max_length=100, default='-')
    thursday_lunch = models.CharField(max_length=100, default='-')
    friday_lunch = models.CharField(max_length=100, default='-')
    saturday_lunch = models.CharField(max_length=100, default='-')
    sunday_lunch = models.CharField(max_length=100, default='-')

    monday_dinner = models.CharField(max_length=100, default='-')
    tuesday_dinner = models.CharField(max_length=100, default='-')
    wednesday_dinner = models.CharField(max_length=100, default='-')
    thursday_dinner = models.CharField(max_length=100, default='-')
    friday_dinner = models.CharField(max_length=100, default='-')
    saturday_dinner = models.CharField(max_length=100, default='-')
    sunday_dinner = models.CharField(max_length=100, default='-')

    credit = models.FloatField(default=-30)
