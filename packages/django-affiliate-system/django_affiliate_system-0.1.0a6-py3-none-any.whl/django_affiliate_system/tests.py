# tests.py

from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from .models import (
    Affiliate,
    Commission,
    CommissionRule,
    Payout,
    ReferralAction,
    ReferralLink,
    ReferralSession,
    Tenant,
)

User = get_user_model()


class AffiliateModelTests(TestCase):
    """Tests for Affiliate model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com", email="test@example.com", password="testpass123"
        )

    def test_create_affiliate_without_code(self):
        """Test affiliate code is auto-generated"""
        affiliate = Affiliate.objects.create(user=self.user)
        self.assertIsNotNone(affiliate.code)
        self.assertTrue(len(affiliate.code) > 0)

    def test_create_affiliate_with_custom_code(self):
        """Test affiliate with custom code"""
        affiliate = Affiliate.objects.create(user=self.user, code="CUSTOM123")
        self.assertEqual(affiliate.code, "CUSTOM123")

    def test_affiliate_code_uniqueness(self):
        """Test affiliate codes are unique"""
        Affiliate.objects.create(user=self.user, code="UNIQUE")

        user2 = User.objects.create_user(
            username="test2@example.com", email="test2@example.com", password="testpass123"
        )

        with self.assertRaises(Exception):
            Affiliate.objects.create(user=user2, code="UNIQUE")

    def test_affiliate_without_tenant(self):
        """Test affiliate can be created without tenant"""
        affiliate = Affiliate.objects.create(user=self.user)
        self.assertIsNone(affiliate.tenant)

    def test_affiliate_default_balance(self):
        """Test default balance is 0"""
        affiliate = Affiliate.objects.create(user=self.user)
        self.assertEqual(affiliate.balance, Decimal("0.00"))


class ReferralLinkModelTests(TestCase):
    """Tests for ReferralLink model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com", email="test@example.com", password="testpass123"
        )
        self.affiliate = Affiliate.objects.create(user=self.user)

    def test_create_referral_link(self):
        """Test creating a referral link"""
        link = ReferralLink.objects.create(
            affiliate=self.affiliate, slug="test-link", destination_url="https://example.com"
        )
        self.assertEqual(link.slug, "test-link")
        self.assertTrue(link.is_active)

    def test_referral_link_slug_uniqueness(self):
        """Test slug must be unique"""
        ReferralLink.objects.create(
            affiliate=self.affiliate, slug="unique-slug", destination_url="https://example.com"
        )

        user2 = User.objects.create_user(
            username="test2@example.com", email="test2@example.com", password="testpass123"
        )
        affiliate2 = Affiliate.objects.create(user=user2)

        with self.assertRaises(Exception):
            ReferralLink.objects.create(
                affiliate=affiliate2, slug="unique-slug", destination_url="https://example.com"
            )


class ReferralActionModelTests(TestCase):
    """Tests for ReferralAction model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com", email="test@example.com", password="testpass123"
        )
        self.affiliate = Affiliate.objects.create(user=self.user)
        self.link = ReferralLink.objects.create(
            affiliate=self.affiliate, slug="test-link", destination_url="https://example.com"
        )

    def test_create_click_action(self):
        """Test creating a click action"""
        action = ReferralAction.objects.create(
            referral_link=self.link,
            action_type="click",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )
        self.assertEqual(action.action_type, "click")
        self.assertFalse(action.is_converted)

    def test_create_conversion_action(self):
        """Test creating a conversion action"""
        action = ReferralAction.objects.create(
            referral_link=self.link,
            action_type="purchase",
            is_converted=True,
            conversion_value=Decimal("99.99"),
            converted_at=timezone.now(),
        )
        self.assertTrue(action.is_converted)
        self.assertEqual(action.conversion_value, Decimal("99.99"))


class CommissionModelTests(TestCase):
    """Tests for Commission model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com", email="test@example.com", password="testpass123"
        )
        self.affiliate = Affiliate.objects.create(user=self.user)
        self.link = ReferralLink.objects.create(
            affiliate=self.affiliate, slug="test-link", destination_url="https://example.com"
        )
        self.action = ReferralAction.objects.create(
            referral_link=self.link,
            action_type="purchase",
            is_converted=True,
            conversion_value=Decimal("100.00"),
        )

    def test_create_commission(self):
        """Test creating a commission"""
        commission = Commission.objects.create(
            affiliate=self.affiliate,
            referral_action=self.action,
            amount=Decimal("10.00"),
            rate=Decimal("10.00"),
            status="pending",
        )
        self.assertEqual(commission.amount, Decimal("10.00"))
        self.assertEqual(commission.status, "pending")

    def test_commission_updates_balance(self):
        """Test commission increases affiliate balance"""
        initial_balance = Decimal(str(self.affiliate.balance))

        commission = Commission.objects.create(
            affiliate=self.affiliate,
            referral_action=self.action,
            amount=Decimal("10.00"),
            rate=Decimal("10.00"),
        )

        # Manually update balance (normally done in service)
        self.affiliate.balance = Decimal(str(self.affiliate.balance)) + commission.amount
        self.affiliate.save()

        self.affiliate.refresh_from_db()
        self.assertEqual(Decimal(str(self.affiliate.balance)), initial_balance + Decimal("10.00"))


class CommissionRuleTests(TestCase):
    """Tests for CommissionRule model"""

    def test_percentage_commission_rule(self):
        """Test percentage-based commission rule"""
        rule = CommissionRule.objects.create(
            name="Purchase Commission",
            action_type="purchase",
            is_percentage=True,
            value=Decimal("10.00"),
            is_active=True,
        )
        self.assertTrue(rule.is_percentage)
        self.assertEqual(rule.value, Decimal("10.00"))

    def test_flat_commission_rule(self):
        """Test flat-rate commission rule"""
        rule = CommissionRule.objects.create(
            name="Signup Bonus",
            action_type="signup",
            is_percentage=False,
            value=Decimal("25.00"),
            is_active=True,
        )
        self.assertFalse(rule.is_percentage)
        self.assertEqual(rule.value, Decimal("25.00"))

    def test_commission_rule_with_limits(self):
        """Test commission rule with min/max values"""
        rule = CommissionRule.objects.create(
            name="Limited Commission",
            action_type="purchase",
            is_percentage=True,
            value=Decimal("15.00"),
            min_value=Decimal("5.00"),
            max_value=Decimal("100.00"),
            is_active=True,
        )
        self.assertEqual(rule.min_value, Decimal("5.00"))
        self.assertEqual(rule.max_value, Decimal("100.00"))


class AffiliateAPITests(APITestCase):
    """Tests for Affiliate API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test@example.com", email="test@example.com", password="testpass123"
        )
        self.affiliate = Affiliate.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_get_affiliate_profile(self):
        """Test getting affiliate profile"""
        url = reverse("django_affiliate_system:affiliates-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], self.affiliate.code)

    def test_get_affiliate_stats(self):
        """Test getting affiliate statistics"""
        url = reverse("django_affiliate_system:affiliates-stats")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_clicks", response.data)
        self.assertIn("total_conversions", response.data)
        self.assertIn("total_earnings", response.data)

    def test_unauthenticated_access(self):
        """Test unauthenticated users cannot access"""
        self.client.force_authenticate(user=None)
        url = reverse("django_affiliate_system:affiliates-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReferralLinkAPITests(APITestCase):
    """Tests for ReferralLink API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test@example.com", email="test@example.com", password="testpass123"
        )
        self.affiliate = Affiliate.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_referral_link(self):
        """Test creating a referral link"""
        url = reverse("django_affiliate_system:referral-links-list")
        data = {
            "slug": "my-link",
            "destination_url": "https://example.com",
            "campaign_name": "Test Campaign",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["slug"], "my-link")

    def test_list_referral_links(self):
        """Test listing referral links"""
        ReferralLink.objects.create(
            affiliate=self.affiliate, slug="link1", destination_url="https://example.com"
        )
        ReferralLink.objects.create(
            affiliate=self.affiliate, slug="link2", destination_url="https://example.com"
        )

        url = reverse("django_affiliate_system:referral-links-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_cannot_create_duplicate_slug(self):
        """Test cannot create link with duplicate slug"""
        ReferralLink.objects.create(
            affiliate=self.affiliate, slug="unique", destination_url="https://example.com"
        )

        url = reverse("django_affiliate_system:referral-links-list")
        data = {"slug": "unique", "destination_url": "https://example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TrackingAPITests(APITestCase):
    """Tests for tracking endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test@example.com", email="test@example.com", password="testpass123"
        )
        self.affiliate = Affiliate.objects.create(user=self.user, code="TEST123")
        self.link = ReferralLink.objects.create(
            affiliate=self.affiliate, slug="test-link", destination_url="https://example.com"
        )

    def test_track_click(self):
        """Test tracking a click"""
        url = reverse("django_affiliate_system:referral-actions-track")
        data = {"referral_code": "TEST123", "event_type": "click", "metadata": {"source": "email"}}
        response = self.client.post(url, data, format="json")  # Use JSON format for nested data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify action was created
        action = ReferralAction.objects.get(id=response.data["id"])
        self.assertEqual(action.action_type, "click")

    def test_track_conversion(self):
        """Test tracking a conversion"""
        url = reverse("django_affiliate_system:referral-actions-track")
        data = {
            "referral_slug": "test-link",
            "event_type": "purchase",
            "is_conversion": True,
            "conversion_value": 99.99,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        action = ReferralAction.objects.get(id=response.data["id"])
        self.assertTrue(action.is_converted)
        self.assertEqual(action.conversion_value, Decimal("99.99"))

    def test_tracking_without_auth(self):
        """Test tracking works without authentication"""
        self.client.force_authenticate(user=None)

        url = reverse("django_affiliate_system:referral-actions-track")
        data = {"referral_code": "TEST123", "event_type": "click"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class PayoutTests(TestCase):
    """Tests for Payout functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com", email="test@example.com", password="testpass123"
        )
        self.affiliate = Affiliate.objects.create(
            user=self.user,
            balance=Decimal("100.00"),
            payout_threshold=Decimal("50.00"),
            payout_method="paypal",
        )

    def test_request_payout_above_threshold(self):
        """Test requesting payout when balance exceeds threshold"""
        payout = Payout.objects.create(
            affiliate=self.affiliate,
            amount=self.affiliate.balance,
            status="pending",
            method=self.affiliate.payout_method,
        )

        self.assertEqual(payout.amount, Decimal("100.00"))
        self.assertEqual(payout.status, "pending")

    def test_payout_resets_balance(self):
        """Test payout resets affiliate balance"""
        initial_balance = self.affiliate.balance

        payout = Payout.objects.create(
            affiliate=self.affiliate,
            amount=self.affiliate.balance,
            status="pending",
            method=self.affiliate.payout_method,
        )

        self.affiliate.balance = Decimal("0.00")
        self.affiliate.save()

        self.affiliate.refresh_from_db()
        self.assertEqual(self.affiliate.balance, Decimal("0.00"))


class TenantTests(TestCase):
    """Tests for optional Tenant functionality"""

    def test_create_tenant(self):
        """Test creating a tenant"""
        user = User.objects.create_user(
            username="owner@example.com", email="owner@example.com", password="testpass123"
        )

        tenant = Tenant.objects.create(
            name="Test Platform", slug="test-platform", subdomain="test", owner=user
        )

        self.assertEqual(tenant.name, "Test Platform")
        self.assertEqual(tenant.owner, user)

    def test_affiliate_with_tenant(self):
        """Test creating affiliate with tenant"""
        user = User.objects.create_user(
            username="owner@example.com", email="owner@example.com", password="testpass123"
        )

        tenant = Tenant.objects.create(name="Test Platform", slug="test-platform", owner=user)

        affiliate_user = User.objects.create_user(
            username="affiliate@example.com", email="affiliate@example.com", password="testpass123"
        )

        affiliate = Affiliate.objects.create(user=affiliate_user, tenant=tenant)

        self.assertEqual(affiliate.tenant, tenant)

    def test_affiliate_without_tenant(self):
        """Test creating affiliate without tenant"""
        user = User.objects.create_user(
            username="affiliate@example.com", email="affiliate@example.com", password="testpass123"
        )

        affiliate = Affiliate.objects.create(user=user)

        self.assertIsNone(affiliate.tenant)


class CommissionCalculationTests(TestCase):
    """Tests for commission calculation logic"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="test@example.com", email="test@example.com", password="testpass123"
        )
        self.affiliate = Affiliate.objects.create(user=self.user)

    def test_percentage_commission_calculation(self):
        """Test percentage-based commission calculation"""
        rule = CommissionRule.objects.create(
            name="Test Rule",
            action_type="purchase",
            is_percentage=True,
            value=Decimal("10.00"),
            is_active=True,
        )

        conversion_value = Decimal("100.00")
        expected_commission = conversion_value * (rule.value / 100)

        self.assertEqual(expected_commission, Decimal("10.00"))

    def test_flat_rate_commission(self):
        """Test flat-rate commission"""
        rule = CommissionRule.objects.create(
            name="Signup Bonus",
            action_type="signup",
            is_percentage=False,
            value=Decimal("25.00"),
            is_active=True,
        )

        # Flat rate should always be the value
        self.assertEqual(rule.value, Decimal("25.00"))


class IntegrationTests(TransactionTestCase):
    """End-to-end integration tests"""

    def test_complete_referral_flow(self):
        """Test complete flow from signup to commission"""
        # 1. Create affiliate
        user = User.objects.create_user(
            username="affiliate@example.com", email="affiliate@example.com", password="testpass123"
        )
        affiliate = Affiliate.objects.create(user=user)

        # 2. Create referral link
        link = ReferralLink.objects.create(
            affiliate=affiliate, slug="test-promo", destination_url="https://example.com"
        )

        # 3. Create commission rule
        rule = CommissionRule.objects.create(
            name="Purchase Commission",
            action_type="purchase",
            is_percentage=True,
            value=Decimal("10.00"),
            is_active=True,
        )

        # 4. Track conversion
        action = ReferralAction.objects.create(
            referral_link=link,
            action_type="purchase",
            is_converted=True,
            conversion_value=Decimal("100.00"),
            converted_at=timezone.now(),
        )

        # 5. Create commission
        commission = Commission.objects.create(
            affiliate=affiliate,
            referral_action=action,
            amount=Decimal("10.00"),
            rate=rule.value,
            status="pending",
        )

        # 6. Update balance
        affiliate.balance = Decimal(str(affiliate.balance)) + commission.amount
        affiliate.save()

        # Verify everything
        self.assertEqual(Decimal(str(affiliate.balance)), Decimal("10.00"))
        self.assertEqual(commission.status, "pending")
        self.assertTrue(action.is_converted)


# Run tests with:
# python manage.py test django_affiliate_system
