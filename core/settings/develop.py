from .base import *  # noqa

DEBUG = True
CELERY_TASK_ALWAYS_EAGER = False


DEBUG_TOOLBAR_ENABLED = True

INSTALLED_APPS += [
    "debug_toolbar",
    "querycount",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "querycount.middleware.QueryCountMiddleware",
] + MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1"]