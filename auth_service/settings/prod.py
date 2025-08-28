from .base import *
# DEBUG must be set via env in prod (default False from base)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
