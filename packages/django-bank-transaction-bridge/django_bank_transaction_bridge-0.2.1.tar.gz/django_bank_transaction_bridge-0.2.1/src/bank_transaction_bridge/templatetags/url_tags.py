from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag()
def bank_transaction_bridge_urls():
    return {
        "transaction_list_url": reverse("bank_transaction_bridge:transaction_list"),
        "bank_account_list_url": reverse("bank_transaction_bridge:bank_account_list"),
        "import_mapping_list_url": reverse(
            "bank_transaction_bridge:import_mapping_list"
        ),
        "import_bank_statement_url": reverse(
            "bank_transaction_bridge:import_bank_statement"
        ),
    }
