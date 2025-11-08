"""Pytest configuration and fixtures for django-affiliate-system tests."""

import pytest
from django.contrib.auth import get_user_model

from django_affiliate_system.models import Affiliate, ReferralLink, Tenant

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def owner(db):
    """Create a tenant owner user."""
    return User.objects.create_user(
        username="owner", email="owner@example.com", password="ownerpass123"
    )


@pytest.fixture
def tenant(db, owner):
    """Create a test tenant."""
    return Tenant.objects.create(
        name="Test Tenant",
        slug="test-tenant",
        destination_url="https://example.com",
        owner=owner,
        default_commission_rate=10.0,
        cookie_duration_days=30,
    )


@pytest.fixture
def affiliate(db, tenant, user):
    """Create a test affiliate."""
    return Affiliate.objects.create(
        tenant=tenant,
        user=user,
        code=f"TEST{user.id}",
        is_active=True,
        payout_threshold=50.0,
    )


@pytest.fixture
def referral_link(db, affiliate):
    """Create a test referral link."""
    return ReferralLink.objects.create(
        affiliate=affiliate,
        slug="test-link",
        destination_url=affiliate.tenant.destination_url,
        is_active=True,
    )


@pytest.fixture
def api_client():
    """Create a DRF API client."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def tenant_api_client(api_client, tenant):
    """Create an API client with tenant API key."""
    api_client.credentials(HTTP_X_API_KEY=str(tenant.api_key))
    return api_client
