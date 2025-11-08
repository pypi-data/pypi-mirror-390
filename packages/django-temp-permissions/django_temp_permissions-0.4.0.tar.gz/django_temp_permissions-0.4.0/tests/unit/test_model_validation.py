from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from test_utils.factories import TemporaryPermissionFactory


@pytest.mark.django_db
def test_clean_no_perm_assigned():
    with pytest.raises(ValidationError) as e:
        TemporaryPermissionFactory(permissions=[]).full_clean()

    assert "At least one Permission must be selected." in e.value.messages


@pytest.mark.django_db
def test_start_date_not_after_end_date():
    with pytest.raises(ValidationError) as e:
        TemporaryPermissionFactory(
            end_datetime=timezone.now() - timedelta(days=100),
        ).full_clean()

    assert "End datetime must be after start datetime." in e.value.messages
