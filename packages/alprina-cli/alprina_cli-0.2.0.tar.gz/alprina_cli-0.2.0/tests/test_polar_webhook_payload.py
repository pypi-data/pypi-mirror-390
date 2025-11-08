"""
Test Polar webhook payload parsing.

This test uses the ACTUAL payload structure from Polar.sh documentation
to ensure our webhook handler extracts fields correctly.
"""

import pytest
from typing import Dict, Any


# Real payload from Polar.sh docs
SUBSCRIPTION_CREATED_PAYLOAD = {
    "type": "subscription.created",
    "timestamp": "2023-11-07T05:31:56Z",
    "data": {
        "created_at": "2023-11-07T05:31:56Z",
        "modified_at": "2023-11-07T05:31:56Z",
        "id": "sub_123abc",
        "amount": 10000,
        "currency": "usd",
        "recurring_interval": "month",
        "recurring_interval_count": 1,
        "status": "active",
        "current_period_start": "2023-11-07T05:31:56Z",
        "current_period_end": "2023-12-07T05:31:56Z",
        "trial_start": "2023-11-07T05:31:56Z",
        "trial_end": "2023-11-14T05:31:56Z",
        "cancel_at_period_end": False,
        "canceled_at": None,
        "started_at": "2023-11-07T05:31:56Z",
        "ends_at": None,
        "ended_at": None,
        "customer_id": "cus_456def",
        "product_id": "68443920-6061-434f-880d-83d4efd50fde",  # Developer plan
        "discount_id": None,
        "checkout_id": "checkout_789ghi",
        "seats": 1,
        "metadata": {},
        "custom_field_data": {},
        "customer": {
            "id": "cus_456def",
            "created_at": "2023-11-07T05:31:56Z",
            "modified_at": "2023-11-07T05:31:56Z",
            "metadata": {},
            "external_id": None,
            "email": "malte@joshwagenbach.com",
            "email_verified": True,
            "name": "Malte Wagenbach",
            "billing_address": None,
            "tax_id": None,
            "organization_id": None,
            "deleted_at": None,
            "avatar_url": None
        },
        "product": {
            "id": "68443920-6061-434f-880d-83d4efd50fde",
            "created_at": "2023-11-07T05:31:56Z",
            "modified_at": "2023-11-07T05:31:56Z",
            "name": "Developer Plan",
            "description": "Perfect for individual developers",
            "recurring_interval": "month",
            "recurring_interval_count": 1,
            "is_recurring": True,
            "is_archived": False,
            "organization_id": "org_123",
            "metadata": {},
            "prices": [],
            "benefits": [],
            "medias": [],
            "attached_custom_fields": []
        }
    }
}


def test_extract_customer_email():
    """Test that we can correctly extract customer email from payload."""
    data = SUBSCRIPTION_CREATED_PAYLOAD["data"]

    # WRONG WAY (what our code currently does - this will be None!)
    customer_email_wrong = data.get("customer_email")
    assert customer_email_wrong is None, "customer_email should NOT exist at root!"

    # CORRECT WAY (what we should do)
    customer = data.get("customer", {})
    customer_email_correct = customer.get("email")
    assert customer_email_correct == "malte@joshwagenbach.com"


def test_extract_product_id():
    """Test that we can extract product_id directly."""
    data = SUBSCRIPTION_CREATED_PAYLOAD["data"]

    product_id = data.get("product_id")
    assert product_id == "68443920-6061-434f-880d-83d4efd50fde"


def test_extract_product_name_from_nested_object():
    """Test that product.name is in nested product object, not from API call."""
    data = SUBSCRIPTION_CREATED_PAYLOAD["data"]

    # Product object is already in the payload!
    product = data.get("product", {})
    product_name = product.get("name")
    assert product_name == "Developer Plan"

    # We DON'T need to call polar_service.get_subscription() for product name
    # It's already here!


def test_extract_all_required_fields():
    """Test extracting all fields we need for tier assignment."""
    data = SUBSCRIPTION_CREATED_PAYLOAD["data"]

    # Required fields
    subscription_id = data.get("id")
    customer_id = data.get("customer_id")
    product_id = data.get("product_id")
    status = data.get("status")

    # Customer email from nested object
    customer = data.get("customer", {})
    customer_email = customer.get("email")

    # Product name from nested object (fallback if product_id mapping fails)
    product = data.get("product", {})
    product_name = product.get("name")

    assert subscription_id == "sub_123abc"
    assert customer_id == "cus_456def"
    assert product_id == "68443920-6061-434f-880d-83d4efd50fde"
    assert status == "active"
    assert customer_email == "malte@joshwagenbach.com"
    assert product_name == "Developer Plan"


def test_tier_detection_should_use_product_id_first():
    """Test that tier detection uses product_id, not product name."""
    from alprina_cli.api.services.polar_service import polar_service

    data = SUBSCRIPTION_CREATED_PAYLOAD["data"]
    product_id = data.get("product_id")

    # Use product_id for tier detection (faster, more reliable)
    tier = polar_service.get_tier_from_product_id(product_id)
    assert tier == "developer"

    # Fallback to product name if product_id not in map
    product = data.get("product", {})
    product_name = product.get("name")
    tier_from_name = polar_service.get_tier_from_product(product_name)
    assert tier_from_name == "developer"


def test_subscription_updated_payload():
    """Test subscription.updated uses same structure."""
    payload = {
        "type": "subscription.updated",
        "timestamp": "2023-11-07T05:31:56Z",
        "data": {
            "id": "sub_123abc",
            "customer_id": "cus_456def",
            "product_id": "fa25e85e-5295-4dd5-bdd9-5cb5cac15a0b",  # Pro plan
            "status": "active",
            "customer": {
                "email": "malte@joshwagenbach.com"
            },
            "product": {
                "name": "Pro Plan"
            }
        }
    }

    data = payload["data"]

    # Extract email correctly
    customer_email = data.get("customer", {}).get("email")
    assert customer_email == "malte@joshwagenbach.com"

    # Extract product_id for tier
    product_id = data.get("product_id")
    from alprina_cli.api.services.polar_service import polar_service
    tier = polar_service.get_tier_from_product_id(product_id)
    assert tier == "pro"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
