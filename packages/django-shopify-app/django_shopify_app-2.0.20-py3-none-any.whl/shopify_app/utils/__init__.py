import base64
import hashlib
import hmac
import importlib
from django.apps import apps
from django.conf import settings
from django.shortcuts import redirect, render


def get_shop_model():
    Model = apps.get_model(settings.SHOPIFY_SHOP_MODEL)
    return Model


def get_shop(shopify_domain):
    Model = get_shop_model()
    shop = Model.objects.get(shopify_domain=shopify_domain)
    return shop


def get_auth_shop(shopify_domain):
    Model = get_shop_model()
    try:
        shop = Model.objects.get(shopify_domain=shopify_domain)
    except Model.DoesNotExist:
        shop = Model()

    return shop


def get_function_from_string(string):
    func_name = string.rsplit(".")[-1]
    location = string.replace(f".{func_name}", "")
    module = importlib.import_module(location)
    if not hasattr(module, func_name):
        raise AttributeError(f"Module {module} does not have function {func_name}")
    func = getattr(module, func_name)
    return func


def webhook_request_is_valid(received_hmac, message, shop=None):
    if shop:
        secret = shop.shopify_app_api_secret.encode("utf-8")
    else:
        secret = settings.SHOPIFY_API_SECRET.encode("utf-8")

    digest = hmac.new(secret, message, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest)
    received_hmac = received_hmac.encode("utf-8")
    is_valid = hmac.compare_digest(computed_hmac, received_hmac)
    return is_valid


def crm_update_all_shops_billing_status(
    update_shop_billing_status_task=None,
    delay_between_tasks=10,
):
    Model = get_shop_model()
    shops = Model.objects.all()
    index = 0
    for shop in shops:
        if update_shop_billing_status_task:
            update_shop_billing_status_task.apply_async(
                args=[shop.id], countdown=delay_between_tasks * index
            )
        else:
            crm_update_shop_billing_status(shop.id)

        index += 1


def crm_update_shop_billing_status(shop_id):
    Model = get_shop_model()
    shop = Model.objects.get(id=shop_id)

    charge_price = 0
    response = shop.get(
        f"/admin/api/{shop.api_version}/recurring_application_charges.json?status=active"
    )

    if response.status_code == 200:
        charges = response.json()["recurring_application_charges"]
        for charge in charges:
            if charge["status"] == "active" and charge["test"] == False:
                charge_price = float(charge["price"])
                break

    shop.crm_on_billing_plan_change(charge_price)


def app_proxy_url_builder(request, path):
    shop = get_shop(request.GET.get("shop"))
    path_prefix = request.GET.get("path_prefix")
    return f"https://{shop.shopify_domain}{path_prefix}{path}"


def app_proxy_redirect(request, path):
    return redirect(app_proxy_url_builder(request, path))


def liquid_render(request, template, context):
    response = render(request, template, context)
    response["Content-Type"] = "application/liquid"
    return response


def shopify_app_redirect(request, url, shop):
    if request.GET.get("embedded"):
        context = {
            "api_key": shop.shopify_app_api_key,
            "host": request.GET.get("host"),
            "redirect": url,
        }
        return render(request, "shopify_app/index.html", context=context)
    else:
        return redirect(url)
