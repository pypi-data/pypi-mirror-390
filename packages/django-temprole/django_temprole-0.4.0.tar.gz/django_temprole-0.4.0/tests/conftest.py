from datetime import timedelta

import pytest
from django.utils import timezone

from test_utils.factories import UserFactory, TemporaryRoleFactory, GroupFactory


@pytest.fixture
def regular_user(db):
    return UserFactory(is_staff=True)


@pytest.fixture
def group():
    return GroupFactory()


@pytest.fixture
def expired_temporary_role():
    base_time = timezone.now()

    return TemporaryRoleFactory(
        start_datetime=base_time - timedelta(hours=5), end_datetime=base_time - timedelta(hours=1)
    )
