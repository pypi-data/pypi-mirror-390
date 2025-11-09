from django.conf import settings


DEFAULTS = {
"BASE_CURRENCY": "INR",
"TIMEZONE": "Asia/Kolkata",
"AUTO_POST_ON_CREATE": True, # API: auto post entry when created
"ALLOW_UNPOST": False, # Only reversal entries are allowed
}


FINACC = getattr(settings, "FINACC", {})




def get(key: str):
    return FINACC.get(key, DEFAULTS.get(key))