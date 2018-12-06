"""reserve_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from dining.views import signup, login, home, userdiningdata_wizard, logout_view, contact_us, prefer_food, dashboard, payment, prefer_food_dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', signup),
    path('login/', login),
    path('', home),
    path('contact_us', contact_us),
    path('wizard/', userdiningdata_wizard),
    path('logout/', logout_view),
    path('prefered_food/', prefer_food),
    path('dashboard/', dashboard),
    path('payment/', payment),
    path('prefered_food/change/', prefer_food_dashboard)
]
