from django.apps import AppConfig
from django.conf import settings


class ShopifyAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shopify_app"

    SHOPIFY_API_KEY = settings.SHOPIFY_API_KEY
    SHOPIFY_API_SECRET = settings.SHOPIFY_API_SECRET
    APP_URL = settings.SHOPIFY_APP_HOST.replace("https://", "")

    APP_HOST = settings.SHOPIFY_APP_HOST

    WEBHOOK_HOST = getattr(settings, "SHOPIFY_WEBHOOK_HOST", APP_HOST)
    WEBHOOK_TOPICS = getattr(settings, "SHOPIFY_WEBHOOK_TOPICS", [])

    SHOPIFY_API_VERSION = getattr(settings, "SHOPIFY_API_VERSION", "2022-04")
    SHOPIFY_API_SCOPES = getattr(settings, "SHOPIFY_APP_SCOPES", [])

    def ready(self):
        return super().ready()
