from django.urls import path, include

from . import views

app_name = 'shopify_app'

urlpatterns = [
    path(
        'gdpr-webhooks/customer-data-request',
        views.MandatoryWebhooksView.as_view(topic='customer_data_request')
    ),
    path(
        'gdpr-webhooks/customer-data-erasure',
        views.MandatoryWebhooksView.as_view(topic='customer_data_erasure')
    ),
    path(
        'gdpr-webhooks/shop-data-erasure',
        views.MandatoryWebhooksView.as_view(topic='shop_data_erasure')
    ),
    path('webhooks', views.WebhooksView.as_view(), name='webhooks'),
]
