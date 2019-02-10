from django.contrib import admin

from order.models import Invoice, RestaurantMenu, RestaurantUniversityCoverage, InvoicePendingPayment, Restaurant, \
    FoodUser

admin.site.register(Invoice)
admin.site.register(RestaurantMenu)
admin.site.register(RestaurantUniversityCoverage)
admin.site.register(InvoicePendingPayment)
admin.site.register(FoodUser)
admin.site.register(Restaurant)
