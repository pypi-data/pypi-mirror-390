"""Models for django-temprole.

This module provides models for managing temporary roles in Django,
allowing administrators to grant time-limited groups to users.
"""

import datetime
import typing
from datetime import timedelta

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model

User = get_user_model()  # noqa


if typing.TYPE_CHECKING:
    from django.db.models import QuerySet


class TemporaryRoleQuerySet(models.QuerySet):
    """Custom chained queryset for TemporaryPermission."""

    def get_active_roles(
        self, user: User | None = None, at: datetime.datetime | None = None
    ) -> "QuerySet[TemporaryRole]":
        """Return the temporary roles granted.

        :argument user: If provided it filter results only for the Django user.
        :argument at: If provided it filter results only for the given datetime.
        """
        base_qs = TemporaryRole.objects.all()
        if user is not None and not user.is_superuser:
            base_qs = base_qs.filter(user=user)
        if at is not None:
            base_qs = base_qs.filter(
                Q(start_datetime__lte=at) | Q(start_datetime__isnull=True),
                Q(end_datetime__gte=at) | Q(end_datetime__isnull=True),
            )

        return base_qs.distinct()

    def get_active_groups(self, user: User | None = None, at: datetime.datetime | None = None) -> "QuerySet[Group]":
        """Similar to get_active_roles, but returns the groups granted instead."""
        base_qs = Group.objects.filter(temporary_grants__isnull=False)
        if user is not None and not user.is_superuser:
            base_qs = base_qs.filter(temporary_grants__user=user)
        if at is not None:
            base_qs = base_qs.filter(
                Q(temporary_grants__start_datetime__lte=at) | Q(temporary_grants__start_datetime__isnull=True),
                Q(temporary_grants__end_datetime__gte=at) | Q(temporary_grants__end_datetime__isnull=True),
            )

        return base_qs.distinct()


class TemporaryRole(models.Model):
    """Model persisting a role validity period for a User.

    Attributes:
        start_datetime: When the temporary role becomes active
        end_datetime: When the temporary role expires
        notes: Optional notes about why the role was granted

    """

    user = models.ForeignKey(User, related_name="temporary_roles", on_delete=models.CASCADE)

    group = models.ForeignKey(
        Group,
        related_name="temporary_grants",
        help_text=_("The role being granted temporarily"),
        on_delete=models.CASCADE,
    )

    start_datetime = models.DateTimeField(
        help_text=_("Date and time when the role becomes active"),
        blank=True,
        null=True,
    )
    end_datetime = models.DateTimeField(
        help_text=_("Date and time when the role expires"),
        blank=True,
        null=True,
    )
    notes = models.TextField(blank=True, default="", help_text=_("Optional notes about this temporary role"))

    objects = TemporaryRoleQuerySet().as_manager()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["user", "group"],
                name="unique_temporary_role",
            )
        ]

    def __str__(self) -> str:  # noqa: D102
        return f"{self.user} ({self.group})"

    def save(self, *args: typing.ParamSpecArgs, **kwargs: typing.ParamSpecKwargs) -> None:
        """Invoke full_clean and save the temporary role."""
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """Perform basic validation for temporary role."""
        super().clean()
        if not (self.start_datetime or self.end_datetime):
            raise ValidationError({"__all__": _("You need at least one of either Start or End date")})

        if self.start_datetime and self.end_datetime and self.start_datetime + timedelta(seconds=1) > self.end_datetime:
            raise ValidationError({"__all__": _("Start date must be before end date")})
