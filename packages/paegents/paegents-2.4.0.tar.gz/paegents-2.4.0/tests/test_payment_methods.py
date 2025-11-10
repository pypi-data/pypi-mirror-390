import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_payments import (
    build_card_payment_method,
    build_braintree_payment_method,
    build_stablecoin_payment_method,
)


def test_build_card_payment_method_defaults():
    payload = build_card_payment_method()
    data = payload.to_dict()
    assert data["rail"] == "card"
    assert data["provider"] == "stripe"
    assert "extra" not in data


def test_build_braintree_payment_method_merges_descriptor():
    payload = build_braintree_payment_method(
        customer_id="cust_123",
        merchant_account_id="merchant_456",
        supplier_domain="example.com",
        descriptor={"name": "Demo", "phone": "123"},
    )
    data = payload.to_dict()
    assert data["rail"] == "braintree"
    assert data["provider"] == "braintree"
    extra = data["extra"]
    assert extra["customer_id"] == "cust_123"
    assert extra["merchant_account_id"] == "merchant_456"
    assert extra["supplier_domain"] == "example.com"
    assert extra["descriptor_name"] == "Demo"
    assert extra["descriptor_phone"] == "123"


def test_build_stablecoin_payment_method_includes_required_fields():
    payload = build_stablecoin_payment_method(
        payer_private_key="0xabc",
        destination_wallet="0xdestination",
        additional_extra={"token_decimals": 6},
    )
    data = payload.to_dict()
    assert data["rail"] == "stablecoin"
    assert data["wallet_address"] == "0xdestination"
    extra = data["extra"]
    assert extra["payer_private_key"].startswith("0x")
    assert extra["network"] == "base-sepolia"
    assert extra["token_decimals"] == 6
