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

from dining.views import signup, login, home, userdiningdata_wizard, logout_view, contact_us, prefer_food, dashboard, \
    payment, prefer_food_dashboard, change_info, change_info_dining, change_days, CustomReset, CustomResetDone, \
    CustomResetConfirm, CustomResetComplete, self_id, send_request, verify, dashboard_mobile, login_mobile

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
    path('prefered_food/change/', prefer_food_dashboard),
    path('changeinfo/', change_info),
    path('change_dining_info/', change_info_dining),
    path('change_days/', change_days),
    path('password_reset/', CustomReset.as_view(), name='password_reset'),
    path('password_reset/done/', CustomResetDone.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomResetConfirm.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomResetComplete.as_view(), name='password_reset_complete'),
    path('self_select/', self_id),
    path('payment/request/', send_request, name='request'),
    path('payment/verify/', verify, name='verify'),
    path('dashboard_mobile/', dashboard_mobile),
    path('login_mobile/', login_mobile),

]

# , {'template_name': 'dining/templates/reset_password.html'
