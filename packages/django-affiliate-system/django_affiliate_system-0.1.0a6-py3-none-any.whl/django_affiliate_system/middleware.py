# middleware.py
import logging

from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from .config import get_config
from .models import Tenant

logger = logging.getLogger(__name__)


class CORSMiddleware(MiddlewareMixin):
    """
    Simple CORS middleware for affiliate tracking.
    Only needed if you're tracking from different domains.
    """

    def process_request(self, request):
        if request.method == "OPTIONS":
            response = HttpResponse()
            self._add_cors_headers(request, response)
            response.status_code = 200
            return response
        return None

    def process_response(self, request, response):
        self._add_cors_headers(request, response)
        return response

    def _add_cors_headers(self, request, response):
        config = get_config()
        allowed_origins = config.get("ALLOWED_CORS_ORIGINS", [])

        if not allowed_origins:
            return

        origin = request.headers.get("Origin")

        if origin in allowed_origins:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-Requested-With"
            )
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Max-Age"] = "86400"


class TenantMiddleware(MiddlewareMixin):
    """
    Optional middleware to set tenant context based on subdomain.
    Only active when ENABLE_MULTI_TENANCY is True.
    """

    def process_request(self, request):
        config = get_config()

        # Skip if multi-tenancy is disabled
        if not config.get("ENABLE_MULTI_TENANCY", False):
            request.tenant = None
            return

        # Skip if already set by authentication
        if hasattr(request, "tenant") and request.tenant:
            logger.debug("Tenant already set by authentication")
            return

        # Try to extract tenant from subdomain
        host = request.get_host().split(":")[0]  # Remove port if present

        if "." in host:
            subdomain = host.split(".")[0]

            # Skip www and common subdomains
            if subdomain in ["www", "api", "admin"]:
                request.tenant = None
                return

            try:
                tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
                request.tenant = tenant
                logger.debug(f"Tenant set from subdomain: {tenant}")
            except Tenant.DoesNotExist:
                logger.debug(f"No tenant found for subdomain: {subdomain}")
                request.tenant = None
        else:
            request.tenant = None


class AffiliateTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to handle affiliate tracking via cookies.
    Attaches affiliate context to request if ref cookie exists.
    """

    def process_request(self, request):
        # Check for referral code in cookies
        ref_code = request.COOKIES.get("ref_code")

        if not ref_code:
            # Check tenant-specific cookie if tenant exists
            if hasattr(request, "tenant") and request.tenant:
                cookie_name = f"ref_{request.tenant.slug}"
                ref_code = request.COOKIES.get(cookie_name)

        if ref_code:
            # Store in request for later use (e.g., in signup signal)
            request.affiliate_ref_code = ref_code
            logger.debug(f"Affiliate ref code found: {ref_code}")
