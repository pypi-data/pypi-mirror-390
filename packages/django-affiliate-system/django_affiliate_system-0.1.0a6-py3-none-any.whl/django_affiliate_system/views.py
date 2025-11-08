import logging
from datetime import timedelta

from django.conf import settings
from django.db.models import Count, Q, Sum
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views import View

from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Affiliate,
    Commission,
    CommissionRule,
    Payout,
    ReferralAction,
    ReferralLink,
    Tenant,
)
from .permissions import IsAffiliate, IsAffiliateOrTenantOwner, IsTenantOwner
from .serializers import (
    AffiliateSerializer,
    CommissionRuleSerializer,
    CommissionSerializer,
    PayoutSerializer,
    ReferralActionSerializer,
    ReferralLinkSerializer,
    TenantSerializer,
)
from .services.tracking import process_tracking_event

logger = logging.getLogger(__name__)


class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenants (optional multi-tenancy feature).
    Only accessible by tenant owners and superusers.
    """

    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Tenant.objects.all()
        return Tenant.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Automatically set the creator as owner"""
        serializer.save(owner=self.request.user)


class AffiliateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing affiliate profiles.
    Affiliates can view/edit their own profile.
    Tenant owners can view all their affiliates.
    """

    serializer_class = AffiliateSerializer
    permission_classes = [IsAffiliateOrTenantOwner]

    def get_queryset(self):
        user = self.request.user

        # Superusers see everything
        if user.is_superuser:
            return Affiliate.objects.all()

        # Tenant owners see their tenant's affiliates
        tenant = getattr(self.request, "tenant", None)
        if tenant and tenant.owner == user:
            queryset = Affiliate.objects.filter(tenant=tenant)
        else:
            # Regular affiliates only see themselves
            queryset = Affiliate.objects.filter(user=user)

        return queryset.select_related("user", "tenant")

    def list(self, request, *args, **kwargs):
        """
        Override list to return single object for non-admin affiliates
        """
        queryset = self.filter_queryset(self.get_queryset())

        # If user is just viewing their own profile, return single object
        if not request.user.is_superuser:
            tenant = getattr(request, "tenant", None)
            if not (tenant and tenant.owner == request.user):
                # This is an affiliate viewing their own data
                instance = queryset.first()
                if not instance:
                    return Response(
                        {"detail": "No affiliate profile found for this user"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                serializer = self.get_serializer(instance)
                return Response(serializer.data)

        # Admin/tenant owner gets paginated list
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """
        Get affiliate statistics for the authenticated user.

        Query params:
            - date_from: Start date (ISO format)
            - date_to: End date (ISO format)
            - tracking_method: Filter by 'code' or 'link' (optional)
        """
        try:
            affiliate = Affiliate.objects.get(user=request.user, is_active=True)
        except Affiliate.DoesNotExist:
            return Response(
                {"detail": "Affiliate profile not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Get date range (default to last 30 days)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        if date_from := request.query_params.get("date_from"):
            start_date = parse_datetime(date_from) or start_date
        if date_to := request.query_params.get("date_to"):
            end_date = parse_datetime(date_to) or end_date

        # CHANGED: Filter by affiliate directly (covers both code and link tracking)
        actions = ReferralAction.objects.filter(
            affiliate=affiliate, timestamp__range=[start_date, end_date]
        )

        # Optional: Filter by tracking method
        tracking_method = request.query_params.get("tracking_method")
        if tracking_method == "code":
            actions = actions.filter(referral_link__isnull=True)
        elif tracking_method == "link":
            actions = actions.filter(referral_link__isnull=False)

        # Calculate statistics
        stats = {
            "total_clicks": actions.filter(action_type="click").count(),
            "total_page_views": actions.filter(action_type="page_view").count(),
            "total_signups": actions.filter(action_type="signup").count(),
            "total_conversions": actions.filter(is_converted=True).count(),
        }

        # Breakdown by tracking method
        stats["tracking_breakdown"] = {
            "code_based": {
                "clicks": actions.filter(action_type="click", referral_link__isnull=True).count(),
                "conversions": actions.filter(
                    is_converted=True, referral_link__isnull=True
                ).count(),
            },
            "link_based": {
                "clicks": actions.filter(action_type="click", referral_link__isnull=False).count(),
                "conversions": actions.filter(
                    is_converted=True, referral_link__isnull=False
                ).count(),
            },
        }

        # Calculate conversion rate
        if stats["total_clicks"] > 0:
            stats["conversion_rate"] = round(
                stats["total_conversions"] / stats["total_clicks"] * 100, 2
            )
        else:
            stats["conversion_rate"] = 0

        # Commission stats
        commissions = Commission.objects.filter(affiliate=affiliate)
        stats["total_earnings"] = commissions.aggregate(total=Sum("amount"))["total"] or 0
        stats["pending_earnings"] = (
            commissions.filter(status="pending").aggregate(total=Sum("amount"))["total"] or 0
        )
        stats["paid_earnings"] = (
            commissions.filter(status="paid").aggregate(total=Sum("amount"))["total"] or 0
        )

        # Total revenue from conversions
        stats["total_revenue"] = (
            actions.filter(is_converted=True).aggregate(total=Sum("conversion_value"))["total"] or 0
        )

        # CHANGED: Top performing links (only for link-based tracking)
        top_links = (
            ReferralLink.objects.filter(affiliate=affiliate)
            .annotate(
                clicks=Count("actions", filter=Q(actions__action_type="click")),
                conversions=Count("actions", filter=Q(actions__is_converted=True)),
                revenue=Sum("actions__conversion_value", filter=Q(actions__is_converted=True)),
            )
            .order_by("-conversions")[:10]
        )

        stats["top_links"] = [
            {
                "slug": link.slug,
                "campaign_name": link.campaign_name,
                "clicks": link.clicks,
                "conversions": link.conversions,
                "revenue": float(link.revenue or 0),
                "conversion_rate": (
                    round(link.conversions / link.clicks * 100, 2) if link.clicks > 0 else 0
                ),
            }
            for link in top_links
        ]

        # NEW: Show affiliate code stats separately
        code_actions = actions.filter(referral_link__isnull=True)
        stats["code_stats"] = {
            "code": affiliate.code,
            "clicks": code_actions.filter(action_type="click").count(),
            "conversions": code_actions.filter(is_converted=True).count(),
            "revenue": code_actions.filter(is_converted=True).aggregate(
                total=Sum("conversion_value")
            )["total"]
            or 0,
        }

        stats["date_range"] = {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        }

        return Response(stats)

    @action(detail=True, methods=["get"], permission_classes=[IsAffiliateOrTenantOwner])
    def performance(self, request, pk=None):
        """
        Get detailed performance metrics for a specific affiliate.
        Available to the affiliate themselves or their tenant owner.

        Query params:
            - date_from: Start date
            - date_to: End date
            - group_by: 'day', 'week', 'month' (default: 'day')
        """
        affiliate = self.get_object()

        # Get date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        if date_from := request.query_params.get("date_from"):
            start_date = parse_datetime(date_from) or start_date
        if date_to := request.query_params.get("date_to"):
            end_date = parse_datetime(date_to) or end_date

        group_by = request.query_params.get("group_by", "day")

        # Time-series data
        actions = ReferralAction.objects.filter(
            affiliate=affiliate, timestamp__range=[start_date, end_date]
        )

        # Group by time period
        if group_by == "day":
            trunc = TruncDay("timestamp")
        elif group_by == "week":
            trunc = TruncWeek("timestamp")
        elif group_by == "month":
            trunc = TruncMonth("timestamp")
        else:
            trunc = TruncDay("timestamp")

        time_series = (
            actions.annotate(period=trunc)
            .values("period")
            .annotate(
                clicks=Count("id", filter=Q(action_type="click")),
                conversions=Count("id", filter=Q(is_converted=True)),
                revenue=Sum("conversion_value", filter=Q(is_converted=True)),
            )
            .order_by("period")
        )

        return Response(
            {
                "affiliate_code": affiliate.code,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "group_by": group_by,
                "time_series": [
                    {
                        "period": item["period"].isoformat(),
                        "clicks": item["clicks"],
                        "conversions": item["conversions"],
                        "revenue": float(item["revenue"] or 0),
                    }
                    for item in time_series
                ],
            }
        )


class ReferralLinkViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing referral links.
    Affiliates can create and manage their own links.
    """

    serializer_class = ReferralLinkSerializer
    permission_classes = [IsAffiliateOrTenantOwner]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return ReferralLink.objects.all()

        tenant = getattr(self.request, "tenant", None)
        if tenant and tenant.owner == user:
            # Tenant owner sees all links for their tenant
            return ReferralLink.objects.filter(affiliate__tenant=tenant)

        # Affiliates see only their own links
        return ReferralLink.objects.filter(affiliate__user=user).select_related("affiliate")

    def perform_create(self, serializer):
        """Create referral link for the authenticated affiliate"""
        try:
            affiliate = Affiliate.objects.get(user=self.request.user, is_active=True)
        except Affiliate.DoesNotExist:
            raise serializers.ValidationError(
                "You must be an active affiliate to create referral links"
            )

        # Verify affiliate belongs to tenant if tenant context exists
        tenant = getattr(self.request, "tenant", None)
        if tenant and affiliate.tenant != tenant:
            raise serializers.ValidationError("Affiliate does not belong to this tenant")

        serializer.save(affiliate=affiliate)


class ReferralActionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing referral actions.
    Provides tracking endpoints for clicks and conversions.
    """

    serializer_class = ReferralActionSerializer
    permission_classes = [IsAffiliateOrTenantOwner]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            queryset = ReferralAction.objects.all()
        else:
            tenant = getattr(self.request, "tenant", None)
            if tenant and tenant.owner == user:
                # Tenant owner sees all actions for their tenant
                queryset = ReferralAction.objects.filter(affiliate__tenant=tenant)
            else:
                # Affiliates see only their own actions
                queryset = ReferralAction.objects.filter(affiliate__user=user)

        # Apply filters
        if referral_link := self.request.query_params.get("referral_link"):
            queryset = queryset.filter(referral_link_id=referral_link)

        # NEW: Filter by affiliate code
        if affiliate_code := self.request.query_params.get("affiliate_code"):
            queryset = queryset.filter(affiliate__code=affiliate_code)

        if action_type := self.request.query_params.get("action_type"):
            queryset = queryset.filter(action_type=action_type)

        if is_converted := self.request.query_params.get("is_converted"):
            queryset = queryset.filter(is_converted=is_converted.lower() == "true")

        # NEW: Filter by tracking method
        if tracking_method := self.request.query_params.get("tracking_method"):
            if tracking_method == "code":
                queryset = queryset.filter(referral_link__isnull=True)
            elif tracking_method == "link":
                queryset = queryset.filter(referral_link__isnull=False)

        return queryset.select_related("affiliate", "affiliate__user", "referral_link")

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def track(self, request):
        """
        Public endpoint for tracking events (clicks, conversions, etc.)

        Required params:
            - referral_code (string) OR referral_slug (string)
            - event_type (string): 'click', 'signup', 'purchase', etc.

        Optional params:
            - conversion_value (decimal): For purchase events
            - session_id (string): For multi-touch attribution
            - use_sessions (boolean): Enable session tracking
            - attribution_model (string): 'first_click' or 'last_click'
            - metadata (object): Additional tracking data
        """
        try:
            action = process_tracking_event(
                request.data,
                request.META,
                use_sessions=request.data.get("use_sessions", False),
                attribution_model=request.data.get("attribution_model", "last_click"),
            )
            return Response(self.get_serializer(action).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CommissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing commissions.
    Affiliates can view their own commissions.
    Tenant owners can manage their affiliates' commissions.
    """

    serializer_class = CommissionSerializer
    permission_classes = [IsAffiliateOrTenantOwner]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            queryset = Commission.objects.all()
        else:
            tenant = getattr(self.request, "tenant", None)
            if tenant and tenant.owner == user:
                # Tenant owner sees all commissions for their tenant
                queryset = Commission.objects.filter(affiliate__tenant=tenant)
            else:
                # Affiliates see only their own commissions
                queryset = Commission.objects.filter(affiliate__user=user)

        # Filter by status if provided
        if status_param := self.request.query_params.get("status"):
            queryset = queryset.filter(status=status_param.lower())

        return queryset.select_related("affiliate", "referral_action")

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a pending commission (admin only)"""
        commission = self.get_object()

        if commission.status != "pending":
            return Response(
                {"detail": f"Commission is already {commission.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        commission.status = "approved"
        commission.save()

        return Response(self.get_serializer(commission).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        """Reject a pending commission (admin only)"""
        commission = self.get_object()

        if commission.status != "pending":
            return Response(
                {"detail": f"Commission is already {commission.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        commission.status = "rejected"
        commission.save()

        # Remove from affiliate balance
        commission.affiliate.balance -= commission.amount
        commission.affiliate.save()

        return Response(self.get_serializer(commission).data)


class PayoutViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payouts.
    Affiliates can request and view their payouts.
    """

    serializer_class = PayoutSerializer
    permission_classes = [IsAffiliateOrTenantOwner]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            queryset = Payout.objects.all()
        else:
            tenant = getattr(self.request, "tenant", None)
            if tenant and tenant.owner == user:
                queryset = Payout.objects.filter(tenant=tenant)
            else:
                queryset = Payout.objects.filter(affiliate__user=user)

        # Filter by status if provided
        if status_param := self.request.query_params.get("status"):
            queryset = queryset.filter(status=status_param.lower())

        return queryset.select_related("affiliate")

    @action(detail=False, methods=["post"], permission_classes=[IsAffiliate])
    def request(self, request):
        """Allow affiliates to request a payout"""
        try:
            affiliate = Affiliate.objects.get(user=request.user, is_active=True)
        except Affiliate.DoesNotExist:
            return Response(
                {"detail": "Affiliate profile not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if affiliate.balance < affiliate.payout_threshold:
            return Response(
                {
                    "detail": (
                        f"Balance (${affiliate.balance}) must be at least "
                        f"${affiliate.payout_threshold}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not affiliate.payout_method:
            return Response(
                {"detail": "Payout method not configured"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create payout request
        payout = Payout.objects.create(
            tenant=affiliate.tenant,
            affiliate=affiliate,
            amount=affiliate.balance,
            status="pending",
            method=affiliate.payout_method,
        )

        # Reset affiliate balance
        affiliate.balance = 0
        affiliate.save()

        return Response(self.get_serializer(payout).data, status=status.HTTP_201_CREATED)


class CommissionRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing commission rules.
    Only accessible by tenant owners and superusers.
    """

    serializer_class = CommissionRuleSerializer
    permission_classes = [IsTenantOwner | IsAdminUser]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return CommissionRule.objects.all()

        tenant = getattr(self.request, "tenant", None)
        if tenant:
            # Return tenant-specific rules and global rules (no tenant)
            return CommissionRule.objects.filter(Q(tenant=tenant) | Q(tenant__isnull=True))

        # If no tenant, return only global rules
        return CommissionRule.objects.filter(tenant__isnull=True)

    def perform_create(self, serializer):
        """Associate rule with tenant if available"""
        tenant = getattr(self.request, "tenant", None)
        serializer.save(tenant=tenant)


class ReferralLinkRedirectView(View):
    """Handle referral link clicks and redirect to destination"""

    def get(self, request, slug):
        try:
            referral_link = ReferralLink.objects.select_related(
                "affiliate", "affiliate__tenant"
            ).get(slug=slug, is_active=True)
        except ReferralLink.DoesNotExist:
            # Redirect to default URL or 404
            default_url = getattr(settings, "AFFILIATE_SYSTEM", {}).get("DEFAULT_REDIRECT_URL", "/")
            return redirect(default_url)

        # Track the click
        ReferralAction.objects.create(
            tenant=referral_link.affiliate.tenant,
            referral_link=referral_link,
            action_type="click",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            referring_url=request.META.get("HTTP_REFERER", ""),
            metadata={"query_params": dict(request.GET)},
        )

        # Set referral cookie
        response = redirect(referral_link.destination_url)

        # Cookie name: either tenant-specific or global
        if referral_link.affiliate.tenant:
            cookie_name = f"ref_{referral_link.affiliate.tenant.slug}"
            cookie_days = referral_link.affiliate.tenant.cookie_duration_days
        else:
            cookie_name = "ref_code"
            cookie_days = getattr(settings, "AFFILIATE_SYSTEM", {}).get("COOKIE_DURATION_DAYS", 30)

        response.set_cookie(
            cookie_name,
            referral_link.affiliate.code,
            max_age=60 * 60 * 24 * cookie_days,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
        )

        return response


class SimpleDebugView(APIView):
    """Simple debug endpoint to test authentication"""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "authenticated": request.user.is_authenticated,
                "user": str(request.user) if request.user.is_authenticated else None,
                "tenant": str(getattr(request, "tenant", None)),
                "affiliate": str(getattr(request, "affiliate", None)),
            }
        )
