from django.apps import AppConfig

from dining.views.zarinpal_online_payment import initialize_client


class DiningConfig(AppConfig):
    name = 'dining'

    def ready(self):
        super().ready()
        try:
            initialize_client()
        except Exception:
            pass
