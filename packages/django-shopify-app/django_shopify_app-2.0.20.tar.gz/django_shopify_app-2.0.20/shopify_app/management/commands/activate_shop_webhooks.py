from django.core.management import BaseCommand, CommandError

from ...utils import get_shop_model


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("shopify_subdomain", type=str)

    def execute(self, *args, **options):
        Shop = get_shop_model()
        shopify_domain = f"{options['shopify_subdomain']}.myshopify.com"

        try:
            shop = Shop.objects.get(shopify_domain=shopify_domain)
        except Shop.DoesNotExist:
            raise CommandError("Shop does not exist")

        shop.update_webhooks()
