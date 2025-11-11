from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model

from django_temprole.models import TemporaryRole
from test_utils.factories import TemporaryRoleFactory, UserFactory

User = get_user_model()


@pytest.mark.parametrize(
    "start_dt, end_dt, expected",
    [
        pytest.param(None, datetime.now() + relativedelta(hours=1), True, id='current'),
        pytest.param(None, datetime.now() - relativedelta(hours=1), False, id='past'),
        pytest.param(datetime.now() + relativedelta(hours=1), None, False, id='future'),
    ],
)
def test_permissions(start_dt, end_dt, expected, regular_user, group, db):
    assert regular_user.user_permissions.count() == 0
    assert regular_user.groups.count() == 0
    assert regular_user.has_perm('auth.view_user') is False
    TemporaryRoleFactory(user=regular_user, group=group, start_datetime=start_dt, end_datetime=end_dt)
    user = User.objects.get(pk=regular_user.id)  # necessary to refresh permissions cache

    assert user.has_perm('auth.view_user') is expected


def test_temproles_manager(regular_user, admin_user, group, db):
    assert TemporaryRole.objects.count() == 0
    temp_role = TemporaryRoleFactory(user=regular_user, group=group)

    assert str(temp_role) == f'{regular_user} ({temp_role.group})'

    assert list(TemporaryRole.objects.get_active_roles()) == [temp_role]
    assert list(TemporaryRole.objects.get_active_groups()) == [temp_role.group]

    assert list(TemporaryRole.objects.get_active_roles(user=regular_user)) == [temp_role]
    assert list(TemporaryRole.objects.get_active_groups(user=regular_user)) == [temp_role.group]
    assert (
        list(TemporaryRole.objects.get_active_roles(user=regular_user, at=datetime.now() - relativedelta(hours=1)))
        == []
    )

    assert list(TemporaryRole.objects.get_active_roles(user=admin_user)) == [temp_role]
    assert list(TemporaryRole.objects.get_active_groups(user=admin_user)) == [temp_role.group]
    assert (
        list(TemporaryRole.objects.get_active_roles(user=admin_user, at=datetime.now() - relativedelta(hours=1))) == []
    )

    other_user = UserFactory()
    assert list(TemporaryRole.objects.get_active_roles(user=other_user)) == []
    assert list(TemporaryRole.objects.get_active_groups(user=other_user)) == []
