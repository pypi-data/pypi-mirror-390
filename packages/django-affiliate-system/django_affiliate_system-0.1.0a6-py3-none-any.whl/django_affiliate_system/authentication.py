# authentication.py
import logging

from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication

from .models import Affiliate, Tenant

logger = logging.getLogger(__name__)
User = get_user_model()


class AffiliateAuthentication(BaseAuthentication):
    """
    Simple authentication that identifies affiliates from authenticated users.
    Uses standard Django/DRF authentication (JWT, Session, etc.)
    """

    def authenticate(self, request):
        # Use Django's standard authentication first
        if not request.user or not request.user.is_authenticated:
            return None

        # Try to attach affiliate and tenant context
        try:
            affiliate = (
                Affiliate.objects.select_related("tenant")
                .filter(user=request.user, is_active=True)
                .first()
            )

            if affiliate:
                request.affiliate = affiliate
                request.tenant = affiliate.tenant  # May be None
                logger.debug(f"Affiliate context set: {affiliate.code}")

        except Exception as e:
            logger.warning(f"Could not set affiliate context: {e}")

        # Return the authenticated user
        return (request.user, None)


class TenantFromSubdomainMixin:
    """
    Mixin to extract tenant from subdomain.
    Can be used with any authentication class.
    """

    def set_tenant_from_subdomain(self, request):
        """Set tenant based on subdomain"""
        if hasattr(request, "tenant") and request.tenant:
            return  # Already set

        host = request.get_host()
        if "." in host:
            subdomain = host.split(".")[0]
            if subdomain and subdomain != "www":
                try:
                    tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
                    request.tenant = tenant
                    logger.debug(f"Tenant set from subdomain: {tenant}")
                except Tenant.DoesNotExist:
                    logger.debug(f"No tenant found for subdomain: {subdomain}")
