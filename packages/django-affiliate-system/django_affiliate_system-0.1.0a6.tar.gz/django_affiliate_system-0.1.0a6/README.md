# Django Affiliate System

A flexible, production-ready Django package for managing affiliate marketing programs with referral tracking, commissions, and payouts.

## Features

- 🔗 **Referral Link Management** - Create and track custom referral links
- 📊 **Detailed Analytics** - Track clicks, conversions, and revenue
- 💰 **Commission System** - Flexible commission rules (percentage or flat rate)
- 💳 **Payout Management** - Handle affiliate payouts with multiple methods
- 🏢 **Optional Multi-Tenancy** - Support multiple platforms with isolated data
- 🎯 **Attribution Models** - First-click, last-click, or custom attribution
- 🔒 **Secure & Production-Ready** - Built with Django best practices

## Installation

```bash
pip install django-affiliate-system
```

## Quick Start

### 1. Add to Installed Apps

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'django_affiliate_system',
]
```

### 2. Configure Settings

```python
# settings.py
AFFILIATE_SYSTEM = {
    # Required
    'DOMAIN_PROTOCOL': 'https',  # or 'http' for local dev
    'DOMAIN': 'yourdomain.com',

    # Optional - Defaults shown
    'DEFAULT_COMMISSION_RATE': 10.0,  # 10%
    'COOKIE_DURATION_DAYS': 30,
    'DEFAULT_REDIRECT_URL': '/',
    'ENABLE_MULTI_TENANCY': False,  # Set True for multi-tenant
    'ENABLE_SESSIONS': False,  # Set True for multi-touch attribution
    'DEFAULT_ATTRIBUTION_MODEL': 'last_click',
    'DEFAULT_PAYOUT_THRESHOLD': 50.0,
    'AUTO_APPROVE_COMMISSIONS': False,

    # CORS (if tracking from different domains)
    'ALLOWED_CORS_ORIGINS': [
        'https://yourdomain.com',
    ],
}
```

### 3. Add Middleware (Optional)

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'django_affiliate_system.middleware.AffiliateTrackingMiddleware',
    # Optional: Only if using multi-tenancy
    # 'django_affiliate_system.middleware.TenantMiddleware',
    # Optional: Only if tracking from different domains
    # 'django_affiliate_system.middleware.CORSMiddleware',
]
```

### 4. Include URLs

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ... other urls
    path('affiliates/', include('django_affiliate_system.urls')),

    # Referral link redirect handler
    path('r/<slug:slug>/',
         'django_affiliate_system.views.ReferralLinkRedirectView.as_view(),
         name='referral-redirect'),
]
```

### 5. Run Migrations

```bash
python manage.py migrate
```

## Usage

### Creating an Affiliate

```python
from django.contrib.auth import get_user_model
from django_affiliate_system.models import Affiliate

User = get_user_model()
user = User.objects.get(email='affiliate@example.com')

# Create affiliate (code is auto-generated if not provided)
affiliate = Affiliate.objects.create(
    user=user,
    code='MYAFFILIATE',  # Optional: auto-generated if omitted
    is_active=True,
    payout_threshold=50.0,
    payout_method='paypal'
)
```

### Creating Referral Links

```python
from django_affiliate_system.models import ReferralLink

link = ReferralLink.objects.create(
    affiliate=affiliate,
    slug='summer-sale-2024',  # Must be unique
    destination_url='https://yourdomain.com/products',
    campaign_name='Summer Sale 2024'
)

# Full referral URL: https://yourdomain.com/?ref=summer-sale-2024
```

### Tracking Events

Use the public API endpoint to track clicks and conversions:

```python
import requests

# Track a click
requests.post('https://yourdomain.com/affiliates/api/referral-actions/track/', json={
    'referral_code': 'MYAFFILIATE',  # or 'referral_slug': 'summer-sale-2024'
    'event_type': 'click',
    'metadata': {
        'source': 'email_campaign',
        'utm_source': 'newsletter'
    }
})

# Track a conversion
requests.post('https://yourdomain.com/affiliates/api/referral-actions/track/', json={
    'referral_code': 'MYAFFILIATE',
    'event_type': 'purchase',
    'is_conversion': True,
    'conversion_value': 99.99,
    'metadata': {
        'order_id': '12345'
    }
})
```

### Setting Commission Rules

```python
from django_affiliate_system.models import CommissionRule

# Percentage-based commission
CommissionRule.objects.create(
    name='Purchase Commission',
    action_type='purchase',
    is_percentage=True,
    value=10.0,  # 10%
    min_value=5.0,  # Minimum $5
    max_value=100.0,  # Maximum $100
    is_active=True,
    priority=1
)

# Flat rate commission
CommissionRule.objects.create(
    name='Signup Bonus',
    action_type='signup',
    is_percentage=False,
    value=25.0,  # $25 flat
    is_active=True,
    priority=1
)
```

### API Endpoints

All endpoints require authentication except tracking endpoints.

#### Affiliate Endpoints

- `GET /affiliates/affiliates/` - List affiliates (or get own profile)
- `GET /affiliates/affiliates/stats/` - Get affiliate statistics
- `POST /affiliates/affiliates/` - Create affiliate (admin only)

#### Referral Link Endpoints

- `GET /affiliates/referral-links/` - List referral links
- `POST /affiliates/referral-links/` - Create referral link
- `GET /affiliates/referral-links/{id}/` - Get referral link details

#### Tracking Endpoints (Public)

- `POST /affiliates/api/referral-actions/track/` - Track any event

#### Commission Endpoints

- `GET /affiliates/commissions/` - List commissions
- `POST /affiliates/commissions/{id}/approve/` - Approve commission (admin)
- `POST /affiliates/commissions/{id}/reject/` - Reject commission (admin)

#### Payout Endpoints

- `GET /affiliates/payouts/` - List payouts
- `POST /affiliates/payouts/request/` - Request payout (affiliate)

### Getting Affiliate Statistics

```python
# Via API
GET /affiliates/affiliates/stats/?date_from=2024-01-01&date_to=2024-12-31

# Response includes:
# - total_clicks, total_conversions, conversion_rate
# - total_earnings, pending_earnings, paid_earnings
# - top_links, traffic_sources, etc.
```

### Frontend Integration

#### JavaScript Tracking Example

```javascript
// Track clicks automatically
document.querySelectorAll("a[data-affiliate-link]").forEach((link) => {
  link.addEventListener("click", async (e) => {
    await fetch("/affiliates/api/referral-actions/track/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        referral_code: e.target.dataset.affiliateCode,
        event_type: "click",
        metadata: {
          page_url: window.location.href,
          referrer: document.referrer,
        },
      }),
    });
  });
});

// Track conversion after purchase
async function trackPurchase(affiliateCode, orderValue) {
  await fetch("/affiliates/api/referral-actions/track/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      referral_code: affiliateCode,
      event_type: "purchase",
      is_conversion: true,
      conversion_value: orderValue,
    }),
  });
}
```

## Advanced Features

### Multi-Tenancy

Enable multi-tenancy to support multiple platforms:

```python
# settings.py
AFFILIATE_SYSTEM = {
    'ENABLE_MULTI_TENANCY': True,
    # ...
}

# Add middleware
MIDDLEWARE = [
    'django_affiliate_system.middleware.TenantMiddleware',
    # ...
]
```

```python
# Create tenants
from django_affiliate_system.models import Tenant

tenant = Tenant.objects.create(
    name='Platform A',
    slug='platform-a',
    subdomain='platforma',  # platforma.yourdomain.com
    destination_url='https://platforma.com',
    owner=admin_user
)
```

### Multi-Touch Attribution

Track user journeys across multiple touchpoints:

```python
# settings.py
AFFILIATE_SYSTEM = {
    'ENABLE_SESSIONS': True,
    'DEFAULT_ATTRIBUTION_MODEL': 'first_click',  # or 'last_click'
}

# Track with session ID
requests.post('/affiliates/api/referral-actions/track/', json={
    'referral_code': 'MYAFFILIATE',
    'event_type': 'click',
    'session_id': 'user-session-123',
    'use_sessions': True
})
```

### Custom Commission Logic

Override commission calculation:

```python
# your_app/services.py
from django_affiliate_system.services.commision import create_commission
from django_affiliate_system.models import Commission

def create_custom_commission(action):
    # Your custom logic here
    commission = Commission.objects.create(
        affiliate=action.referral_link.affiliate,
        referral_action=action,
        amount=calculate_custom_amount(action),
        rate=0,
        status='pending'
    )
    return commission
```

## Admin Interface

The package automatically registers all models in Django admin with:

- List/filter/search functionality
- CSV export
- Inline editing where appropriate

Access at: `/admin/django_affiliate_system/`

## Testing

```bash
# Run tests
python manage.py test django_affiliate_system

# With coverage
coverage run --source='django_affiliate_system' manage.py test
coverage report
```

## Security Considerations

1. **Always use HTTPS in production**
2. **Set secure cookie settings**:
   ```python
   # settings.py
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```
3. **Implement rate limiting** on tracking endpoints
4. **Validate referral codes** to prevent abuse
5. **Use environment variables** for sensitive settings

## Performance Tips

1. **Use database indexes** (already included in models)
2. **Cache affiliate lookups**:

   ```python
   from django.core.cache import cache

   affiliate = cache.get(f'affiliate_{code}')
   if not affiliate:
       affiliate = Affiliate.objects.get(code=code)
       cache.set(f'affiliate_{code}', affiliate, 3600)
   ```

3. **Use select_related/prefetch_related** for queries
4. **Consider async tasks** for commission calculation:

   ```python
   # With Celery
   from celery import shared_task

   @shared_task
   def process_commission(action_id):
       action = ReferralAction.objects.get(id=action_id)
       create_commission(action)
   ```

## Troubleshooting

### Referral codes not being tracked

Check that:

1. `AffiliateTrackingMiddleware` is installed
2. Cookies are enabled in browser
3. Domain matches cookie domain

### Commissions not being created

Verify:

1. Commission rules exist for the action type
2. Rules are active (`is_active=True`)
3. Check logs for errors

### Multi-tenancy not working

Ensure:

1. `ENABLE_MULTI_TENANCY` is `True`
2. `TenantMiddleware` is installed
3. Subdomain DNS is configured correctly

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- Documentation: [docs link]
- Issues: [GitHub issues]
- Email: aayodeji.f@gmail.com

## Changelog

### 1.0.0

- Initial release
- Core affiliate tracking
- Commission system
- Payout management
- Optional multi-tenancy
- Multi-touch attribution
