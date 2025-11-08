# permissions.py
import logging

from rest_framework.permissions import BasePermission

from .models import Affiliate

logger = logging.getLogger(__name__)


class IsAffiliate(BasePermission):
    """Check if user is an active affiliate"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if user has active affiliate profile
        return Affiliate.objects.filter(user=request.user, is_active=True).exists()

    def has_object_permission(self, request, view, obj):
        """Ensure affiliate can only access their own objects"""
        if hasattr(obj, "affiliate"):
            return obj.affiliate.user == request.user
        if hasattr(obj, "user"):
            return obj.user == request.user
        return False


class IsTenantOwner(BasePermission):
    """Check if user owns the tenant (when multi-tenancy is enabled)"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if request has tenant context
        tenant = getattr(request, "tenant", None)
        if not tenant:
            return False

        return tenant.owner == request.user


class IsAffiliateOrTenantOwner(BasePermission):
    """Allow access to affiliates for their own data or tenant owners for their affiliates"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers always have access
        if request.user.is_superuser:
            return True

        # Check if user is tenant owner
        tenant = getattr(request, "tenant", None)
        if tenant and tenant.owner == request.user:
            return True

        # Check if user is an affiliate
        return Affiliate.objects.filter(user=request.user, is_active=True).exists()

    def has_object_permission(self, request, view, obj):
        """Object-level permissions"""
        if request.user.is_superuser:
            return True

        # Tenant owners can access their tenant's data
        tenant = getattr(request, "tenant", None)
        if tenant and tenant.owner == request.user:
            # Check if object belongs to this tenant
            if hasattr(obj, "tenant") and obj.tenant == tenant:
                return True
            if hasattr(obj, "affiliate") and obj.affiliate.tenant == tenant:
                return True

        # Affiliates can only access their own data
        if hasattr(obj, "affiliate"):
            return obj.affiliate.user == request.user
        if hasattr(obj, "user"):
            return obj.user == request.user

        return False


class IsAffiliateOwner(BasePermission):
    """Ensure affiliate can only modify their own data"""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers can do anything
        if request.user.is_superuser:
            return True

        # Affiliate can only access their own profile
        if hasattr(obj, "user"):
            return obj.user == request.user

        # For related objects, check the affiliate relationship
        if hasattr(obj, "affiliate"):
            return obj.affiliate.user == request.user

        return False
