from django.conf import settings

DEFAULTS = {
    "AUTO_POST": True,
}
FA = getattr(settings, "FIXEDASSETS", {})

def get(key: str):
    return FA.get(key, DEFAULTS.get(key))