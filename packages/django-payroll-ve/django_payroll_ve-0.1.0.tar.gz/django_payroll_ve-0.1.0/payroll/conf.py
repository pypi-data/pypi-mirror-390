from django.conf import settings


DEFAULTS = {
"AUTO_POST": True,
}
PAYROLL = getattr(settings, "PAYROLL", {})


def get(key: str):
    return PAYROLL.get(key, DEFAULTS.get(key))