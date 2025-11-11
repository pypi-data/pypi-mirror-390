import json
import logging

from django.conf import settings

from django.apps import apps
from django.urls import reverse
from requests import request

logger = logging.getLogger(__name__)


def update_shop_webhooks(shop):
    deactivate_webhooks(shop)
    activate_webhooks(shop)


def rest_topic_to_graphql(topic):
    return topic.replace("/", "_").upper()


def webhook_activate(shop, topic, callback_url):
    query = """#graphql
        mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
            webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
                webhookSubscription {
                    id
                    topic
                    filter
                    format
                    includeFields
                endpoint {
                    __typename
                    ... on WebhookHttpEndpoint {
                    callbackUrl
                    }
                }
                }
                userErrors {
                    field
                    message
                }
            }
        }
    """

    subscription = {
        "callbackUrl": callback_url,
        "format": "JSON",
    }

    print(json.dumps(subscription, indent=2))

    variables = {
        "topic": rest_topic_to_graphql(topic),
        "webhookSubscription": subscription,
    }

    response = shop.graphql(query=query, variables=variables)

    print(json.dumps(response.json(), indent=2))


def activate_webhooks(shop):
    config = apps.get_app_config("shopify_app")
    webhooks_path = reverse("shopify_app:webhooks")
    callback_url = f"{config.WEBHOOK_HOST}{webhooks_path}"
    for topic in settings.SHOPIFY_WEBHOOK_TOPICS:
        webhook_activate(shop, topic, callback_url)


def deactivate_webhooks(shop):
    response = shop.get("/admin/api/api_version/webhooks.json")
    response.raise_for_status()
    webhooks = response.json()["webhooks"]
    for webhook in webhooks:
        shop.delete_request(f"/admin/api/api_version/webhooks/{webhook['id']}.json")
