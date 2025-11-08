from django.apps import apps
from django.contrib import admin
from django.db.models import CharField, TextField

from django_affiliate_system.utils import AutoTableAdmin, auto_register_models

from . import models

# Register your models here.


# If you need a custom admin for a specific model
class CoreAdmin(AutoTableAdmin):
    exclude_fields = [
        # "password",
    ]


# Auto-register all models in this app
auto_register_models(
    "django_affiliate_system",
    exclude_models=[""],
    # custom_admins={"User": CoreAdmin},
)
