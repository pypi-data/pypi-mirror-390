"""Admin interface for Temporary Role model."""

from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from django_temprole.models import TemporaryRole


@admin.register(TemporaryRole)
class TemporaryRoleAdmin(admin.ModelAdmin):
    """Admin interface for TemporaryRole model.

    Provides a user-friendly interface for managing temporary roles
    with filtering, searching, and display customization.
    """

    list_display = (
        "user",
        "group",
        "start_datetime",
        "end_datetime",
    )
    search_fields = ("user__username", "user__email")
    ordering = ("-start_datetime",)

    list_filter = (
        ("start_datetime", DateFieldListFilter),
        ("end_datetime", DateFieldListFilter),
    )
