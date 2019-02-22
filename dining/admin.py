from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from dining.models import University, UserDiningData, Food, UserPreferableFood, Coins, UserSelfs, ZorroCode, \
    MerchantUser, Merchants, ReservedTable, SamadPrefrredDays
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'phone', 'sex', 'is_paid', 'date_joined']


class UserDiningDataAdmin(admin.ModelAdmin):
    list_display = ['user', 'university', 'is_paid', 'date_joined']
    search_fields = ['user__username', 'dining_username']

    def date_joined(self, instance):
        return instance.user.date_joined

    def is_paid(self, instance):
        return instance.user.is_paid


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(University)
admin.site.register(UserDiningData, UserDiningDataAdmin)
admin.site.register(Food)
admin.site.register(UserPreferableFood)
admin.site.register(Coins)
admin.site.register(UserSelfs)
admin.site.register(ZorroCode)
admin.site.register(Merchants)
admin.site.register(MerchantUser)
admin.site.register(ReservedTable)
admin.site.register(SamadPrefrredDays)

