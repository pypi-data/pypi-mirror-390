from django.conf import settings


DEFAULTS = {
"AUTO_POST_INVOICE": True,
"AUTO_POST_CREDITNOTE": True,
"AUTO_POST_RECEIPT": True,
"AUTO_POST_REFUND": True,
"DEFAULT_TAX_INCLUSIVE": False,
}
SALES = getattr(settings, "SALES", {})


def get(key: str):
    return SALES.get(key, DEFAULTS.get(key))