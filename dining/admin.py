from django.contrib import admin
from dining.models import University, CustomUser, UserDiningData, Food, UserPreferableFood
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'phone', 'sex']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(University)
admin.site.register(UserDiningData)
admin.site.register(Food)
admin.site.register(UserPreferableFood)


