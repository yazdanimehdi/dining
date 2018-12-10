from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from dining.models import University, UserDiningData, Food, UserPreferableFood, Coins, UserSelfs
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'phone', 'sex']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(University)
admin.site.register(UserDiningData)
admin.site.register(Food)
admin.site.register(UserPreferableFood)
admin.site.register(Coins)
admin.site.register(UserSelfs)
