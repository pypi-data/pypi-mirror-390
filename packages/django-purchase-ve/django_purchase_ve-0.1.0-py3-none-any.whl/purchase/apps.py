from django.apps import AppConfig


class PurchaseConfig(AppConfig):
    name = "purchase"
    verbose_name = "Purchase"


    def ready(self):
        from .posting import signals # noqa