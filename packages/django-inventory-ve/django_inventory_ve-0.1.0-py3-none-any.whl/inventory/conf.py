from django.conf import settings


DEFAULTS = {
"DEFAULT_COST_METHOD": "avg", # "fifo" | "avg"
"AUTO_POST_COGS": True, # generate JE for COGS/Asset on issue/receive
"AUTO_HOOK_SALES": True, # connect to django-sales signals if available
"AUTO_HOOK_PURCHASE": True, # (future) connect to purchase signals
}
INV = getattr(settings, "INVENTORY", {})


def get(key: str):
    return INV.get(key, DEFAULTS.get(key))