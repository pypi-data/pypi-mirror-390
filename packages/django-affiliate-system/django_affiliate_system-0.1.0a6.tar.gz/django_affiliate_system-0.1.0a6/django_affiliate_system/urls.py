from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AffiliateViewSet,
    CommissionRuleViewSet,
    CommissionViewSet,
    PayoutViewSet,
    ReferralActionViewSet,
    ReferralLinkRedirectView,
    ReferralLinkViewSet,
    SimpleDebugView,
    TenantViewSet,
)

# Create router for viewsets
router = DefaultRouter()
router.register(r"affiliates", AffiliateViewSet, basename="affiliates")
router.register(r"referral-links", ReferralLinkViewSet, basename="referral-links")
router.register(r"referral-actions", ReferralActionViewSet, basename="referral-actions")
router.register(r"commissions", CommissionViewSet, basename="commissions")
router.register(r"payouts", PayoutViewSet, basename="payouts")
router.register(r"commission-rules", CommissionRuleViewSet, basename="commission-rules")
router.register(r"tenants", TenantViewSet, basename="tenants")

# URL patterns
urlpatterns = [
    # Router URLs
    path("", include(router.urls)),
    # Referral link redirect handler (short URL)
    path("r/<slug:slug>/", ReferralLinkRedirectView.as_view(), name="referral-redirect"),
    # Debug endpoint (for testing authentication)
    path("debug/", SimpleDebugView.as_view(), name="debug"),
]

# Optional: Add app_name for namespacing
app_name = "django_affiliate_system"
