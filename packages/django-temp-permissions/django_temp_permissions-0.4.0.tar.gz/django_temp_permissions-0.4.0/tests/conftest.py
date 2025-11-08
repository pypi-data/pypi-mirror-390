from datetime import timedelta

import pytest
from django.contrib.auth.models import Permission
from django.utils import timezone

from test_utils.factories import UserFactory, TemporaryPermissionFactory


@pytest.fixture
def staff_user():
    return UserFactory(is_staff=True)


@pytest.fixture
def inactive_user():
    return UserFactory(is_active=False)


@pytest.fixture
def expired_temporary_permission():
    base_time = timezone.now()

    return TemporaryPermissionFactory(
        start_datetime=base_time - timedelta(hours=5), end_datetime=base_time - timedelta(hours=1)
    )


@pytest.fixture
def future_temporary_permission():
    base_time = timezone.now()

    return TemporaryPermissionFactory(
        start_datetime=base_time + timedelta(days=1), end_datetime=base_time + timedelta(days=2)
    )


@pytest.fixture
def change_user_perm():
    ret = Permission.objects.get(codename="change_user")
    ret._full_name = ret.content_type.app_label + "." + ret.codename
    return ret
