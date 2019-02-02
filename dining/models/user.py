from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=11)
    sex = models.BooleanField(default=True)
    chat_id = models.BigIntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    reserve = models.BooleanField(default=True)
    code_used = models.CharField(max_length=10, default='-')

    def __str__(self):
        return self.username

