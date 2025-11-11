import hashlib
import hmac
import json
import base64
from functools import cached_property
from django.conf import settings

from django.db import models
from django.apps import apps
import requests

import shopify
from shopify import Session
from crm_events import on_billing_plan_change, on_uninstall, on_login, on_install


from .services.webhooks import update_shop_webhooks, deactivate_webhooks
from .exceptions import ShopifyRequestException


class ShopBase(models.Model):

    shopify_domain = models.CharField(max_length=255, default="")
    shopify_token = models.CharField(max_length=150, default="", blank=True, null=True)
    access_scopes = models.CharField(max_length=250, default="")

    shopify_app_api_key_overwrite = models.CharField(
        max_length=50,
        default="",
        blank=True,
    )
    shopify_app_api_secret_overwrite = models.CharField(
        max_length=50,
        default="",
        blank=True,
    )

    def _prepare_api_call_url(self, path):
        path = path.replace("api_version", self.api_version)
        return f"https://{self.shopify_domain}{path}"

    def get(self, path):
        url = self._prepare_api_call_url(path)
        return requests.get(url, headers=self.request_headers)

    def post(self, path, data):
        url = self._prepare_api_call_url(path)
        return requests.post(url, headers=self.request_headers, data=json.dumps(data))

    def put(self, path, data):
        url = self._prepare_api_call_url(path)
        return requests.put(url, headers=self.request_headers, data=json.dumps(data))

    def patch(self, path, data):
        url = self._prepare_api_call_url(path)
        return requests.patch(url, headers=self.request_headers, data=json.dumps(data))

    def delete_request(self, path):
        url = self._prepare_api_call_url(path)
        return requests.delete(url, headers=self.request_headers)

    @property
    def request_headers(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.shopify_token,
        }
        return headers

    def graphql(self, query=None, variables=None, api_version=None):

        if api_version is None:
            api_version = self.api_version

        url = f"https://{self.shopify_domain}/admin/api/{api_version}/graphql.json"
        data = {"query": query}

        if variables:
            data["variables"] = variables

        return requests.post(url, headers=self.request_headers, json=data)

    @cached_property
    def shopify(self):
        return shopify

    @property
    def shopify_app_api_key(self):
        if self.shopify_app_api_key_overwrite:
            return self.shopify_app_api_key_overwrite
        else:
            return apps.get_app_config("shopify_app").SHOPIFY_API_KEY

    @property
    def shopify_app_api_secret(self):
        if self.shopify_app_api_secret_overwrite:
            return self.shopify_app_api_secret_overwrite
        else:
            return apps.get_app_config("shopify_app").SHOPIFY_API_SECRET

    @property
    def shopify_session(self):
        api_version = apps.get_app_config("shopify_app").SHOPIFY_API_VERSION
        shopify_domain = self.shopify_domain
        return Session.temp(shopify_domain, api_version, self.shopify_token)

    @cached_property
    def api_version(self):
        return apps.get_app_config("shopify_app").SHOPIFY_API_VERSION

    def installed(self, request=None):
        pass

    def update_webhooks(self):
        update_shop_webhooks(self)

    def activate_webhooks(self):
        self.update_webhooks()

    def deactivate_webhooks(self):
        deactivate_webhooks(self)

    def graph(self, operation_name, variables, operations_document):
        with self.shopify_session:
            result = shopify.GraphQL().execute(
                query=operations_document,
                variables=variables,
                operation_name=operation_name,
            )

        result = json.loads(result)
        return result

    @cached_property
    def host(self):
        admin_url = f"{self.shopify_domain}/admin"
        return base64.b64encode(admin_url.encode()).decode()

    def on_user_login(self, user_data, request=None):
        pass

    def app_proxy_request_is_valid(self, request):
        return self.validate_request_hmac(
            request, separator="", signature_name="signature"
        )

    def request_shopify_hmac_is_valid(self, request):
        return self.validate_request_hmac(request)

    def validate_request_hmac(self, request, separator="&", signature_name="hmac"):

        params = request.GET.dict()
        myhmac = params.pop(signature_name)
        line = f"{separator}".join(
            ["%s=%s" % (key, value) for key, value in sorted(params.items())]
        )
        api_secret = self.shopify_app_api_secret
        api_secret = api_secret.encode("utf-8")
        h = hmac.new(api_secret, line.encode("utf-8"), hashlib.sha256)

        return hmac.compare_digest(h.hexdigest(), myhmac)

    def get_shop_data(self):
        response = self.get(f"/admin/api/{self.api_version}/shop.json")
        if response.status_code == 200:
            shop_data = response.json()["shop"]
            return shop_data

        raise ShopifyRequestException(response.status_code, response.text)

    def get_crm_shop_data(self):
        shop_name, domain = self.shopify_domain, self.shopify_domain
        email, phone, country = "", "", ""

        try:
            shop_data = self.get_shop_data()
            shop_name = shop_data["name"]
            email = shop_data["email"]
            phone = shop_data["phone"]
            country = shop_data["country_code"]
        except ShopifyRequestException:
            pass

        return {
            "name": shop_name,
            "domain": domain,
            "email": email,
            "phone": phone,
            "country": country,
        }

    def crm_on_billing_plan_change(self, plan_price):
        on_billing_plan_change(self.get_crm_shop_data(), plan_price)

    def crm_on_uninstall(self, users=[]):
        on_uninstall(self.get_crm_shop_data(), users)

    def crm_on_login(self, user_data):
        on_login(self.get_crm_shop_data(), user_data)

    def crm_on_install(self):
        on_install(self.get_crm_shop_data())

    class Meta:
        abstract = True
