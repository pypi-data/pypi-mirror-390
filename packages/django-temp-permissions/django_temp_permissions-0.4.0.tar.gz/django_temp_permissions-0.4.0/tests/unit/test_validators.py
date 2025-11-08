from datetime import timedelta

from django.utils import timezone

import pytest
from django.core.exceptions import ValidationError

from django_temp_permissions.validators import validate_date_not_in_past
from test_utils.factories import TemporaryPermissionFactory


@pytest.mark.parametrize(
    "time_offset",
    [
        pytest.param(timedelta(seconds=1), id="future_1_second"),
        pytest.param(timedelta(0), id="exactly_now"),
        pytest.param(-timedelta(minutes=4, seconds=59), id="past_4_minutes_just_within_lenience"),
    ],
)
def test_validate_date_not_in_past_accepts_valid_dates(time_offset):
    """Test that dates within the lenience period or in the future are accepted."""
    now = timezone.now()
    validate_date_not_in_past(now + time_offset)


@pytest.mark.parametrize(
    "time_offset",
    [
        pytest.param(-timedelta(hours=1), id="past_1_hour"),
        pytest.param(-timedelta(minutes=5, seconds=1), id="past_5_minutes_just_outside_lenience"),
        pytest.param(-timedelta(minutes=5), id="exactly_at_lenience_boundary"),
    ],
)
def test_validate_date_not_in_past_rejects_invalid_dates(time_offset):
    """Test that dates outside the lenience period are rejected."""
    now = timezone.now()
    with pytest.raises(ValidationError):
        validate_date_not_in_past(now + time_offset)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "field_name,time_offset,expected_errors",
    [
        pytest.param("start_datetime", -timedelta(days=1), 1, id="start_date_1_day_past"),
        pytest.param("start_datetime", -timedelta(hours=2), 1, id="start_date_2_hours_past"),
        pytest.param(
            "end_datetime",
            -timedelta(days=6),
            2,  # Both "date in past" and "end before start" errors
            id="end_date_6_days_past",
        ),
        pytest.param("end_datetime", -timedelta(hours=3), 2, id="end_date_3_hours_past"),
    ],
)
def test_model_rejects_invalid_dates(field_name, time_offset, expected_errors):
    """Test that model validation rejects dates outside the lenience period."""
    now = timezone.now()
    past_date = now + time_offset

    user_temp_permission = TemporaryPermissionFactory(**{field_name: past_date})

    with pytest.raises(ValidationError) as exc_info:
        user_temp_permission.full_clean()

    error_messages = exc_info.value.messages
    assert len(error_messages) == expected_errors
    assert any(f"{past_date} date is in the past." in msg for msg in error_messages)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start_offset,end_offset",
    [
        pytest.param(timedelta(hours=1), timedelta(hours=2), id="both_future"),
        pytest.param(timedelta(minutes=3), timedelta(minutes=10), id="both_within_lenience"),
        pytest.param(-timedelta(minutes=2), timedelta(hours=1), id="start_in_lenience_end_future"),
    ],
)
def test_model_accepts_valid_dates(start_offset, end_offset):
    """Test that model validation accepts dates within the lenience period or future."""
    now = timezone.now()

    user_temp_permission = TemporaryPermissionFactory(
        start_datetime=now + start_offset,
        end_datetime=now + end_offset,
    )

    user_temp_permission.full_clean()
