"""Django temporary permission custom backend."""

from __future__ import annotations

import typing
from datetime import datetime

from django.contrib.auth.backends import BaseBackend, ModelBackend
from django.contrib.auth.models import Permission

from django_temprole.models import TemporaryRole


if typing.TYPE_CHECKING:
    from django.contrib.auth import get_user_model
    from django.db.models import Model, QuerySet

    User = get_user_model()


class TemporaryRolesBackend(BaseBackend):
    """Custom permission backend for temporary roles support."""

    def _get_temprole_permissions(self, user_obj: User, obj: Model = None) -> QuerySet[Permission]:
        return Permission.objects.filter(
            group__in=TemporaryRole.objects.get_active_groups(user=user_obj, at=datetime.now())
        ).distinct()

    def get_all_permissions(self, user_obj: User, obj: Model = None) -> set[str]:
        """Return a set of permission strings the user `user_obj` has from the temporary roles."""
        return {
            *ModelBackend._get_permissions(self, user_obj, obj, "temprole"),
        }
