from django.apps import AppConfig


class SalesConfig(AppConfig):
    name = "sales"
    verbose_name = "Sales"


def ready(self):
    from .posting import signals # noqa