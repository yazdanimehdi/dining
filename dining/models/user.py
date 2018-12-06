from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=10)
    sex = models.BooleanField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.username

