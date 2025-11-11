import pytest

from sila2_interop_communication_tester.grpc_stubs.BasicDataTypesTest_pb2 import (
    EchoTimestampValue_Parameters,
    Get_TimestampValue_Parameters,
)
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import (
    Timestamp,
    Timezone,
)
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_validation_error,
)


def test_echo_timestamp_value_rejects_empty_parameter_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimestampValue should fail with a Validation Error if the parameter message was empty."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(EchoTimestampValue_Parameters())


def test_echo_timestamp_value_rejects_empty_timestamp_message(basicdatatypestest_stub):
    """
    BasicDataTypesTest.EchoTimestampValue should fail with a Validation Error when provided with an empty Timestamp
    message.
    """
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(TimestampValue=Timestamp())
        )


def test_echo_timestamp_value_rejects_timestamp_with_day_too_low(
    basicdatatypestest_stub,
):
    """BasicDataTypesTest.EchoTimestampValue should fail with a Validation Error when provided with day < 1."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=2022,
                    month=8,
                    day=0,
                    hour=12,
                    minute=60,
                    second=56,
                    millisecond=789,
                    timezone=Timezone(),
                )
            )
        )


def test_echo_timestamp_value_rejects_timestamp_with_day_too_high(
    basicdatatypestest_stub,
):
    """BasicDataTypesTest.EchoTimestampValue should fail with a Validation Error when provided with day > 31."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=2022,
                    month=8,
                    day=32,
                    hour=12,
                    minute=60,
                    second=56,
                    millisecond=789,
                    timezone=Timezone(),
                )
            )
        )


def test_echo_timestamp_value_rejects_timestamp_with_month_too_low(
    basicdatatypestest_stub,
):
    """BasicDataTypesTest.EchoTimestampValue should fail with a Validation Error when provided with month < 1."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=2022,
                    month=0,
                    day=5,
                    hour=12,
                    minute=60,
                    second=56,
                    millisecond=789,
                    timezone=Timezone(),
                )
            )
        )


def test_echo_timestamp_value_rejects_timestamp_with_month_too_high(
    basicdatatypestest_stub,
):
    """BasicDataTypesTest.EchoTimestampValue should fail with a Validation Error when provided with month > 12."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=2022,
                    month=13,
                    day=5,
                    hour=12,
                    minute=60,
                    second=56,
                    millisecond=789,
                    timezone=Timezone(),
                )
            )
        )


def test_echo_timestamp_value_rejects_timestamp_with_year_too_low(
    basicdatatypestest_stub,
):
    """BasicDataTypesTest.EchoTimestampValue should fail with a Validation Error when provided with year < 1."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=0,
                    month=8,
                    day=5,
                    hour=12,
                    minute=60,
                    second=56,
                    millisecond=789,
                    timezone=Timezone(),
                )
            )
        )


def test_echo_timestamp_value_rejects_timestamp_with_year_too_high(
    basicdatatypestest_stub,
):
    """BasicDataTypesTest.EchoTimestampValue should fail with a Validation Error when provided with year > 9999."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=10000,
                    month=8,
                    day=5,
                    hour=12,
                    minute=60,
                    second=56,
                    millisecond=789,
                    timezone=Timezone(),
                )
            )
        )


def test_echo_timestamp_value_rejects_timestamp_with_hour_too_high(
    basicdatatypestest_stub,
):
    """BasicDataTypesTest.EchoTimestampValue should fail with a Validation Error when provided with hour > 23."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=2022,
                    month=8,
                    day=5,
                    hour=24,
                    minute=34,
                    second=56,
                    millisecond=789,
                    timezone=Timezone(),
                )
            )
        )


def test_echo_timestamp_value_rejects_timestamp_with_minute_too_high(
    basicdatatypestest_stub,
):
    """BasicDataTypesTest.EchoTimestampValue should fail with a Validation Error when provided with minute > 59."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=2022,
                    month=8,
                    day=5,
                    hour=12,
                    minute=60,
                    second=56,
                    millisecond=789,
                    timezone=Timezone(),
                )
            )
        )


def test_echo_timestamp_value_rejects_timestamp_with_second_too_high(
    basicdatatypestest_stub,
):
    """BasicDataTypesTest.EchoTimestampValue should fail with a Validation Error when provided with second > 59."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=2022,
                    month=8,
                    day=5,
                    hour=12,
                    minute=34,
                    second=60,
                    millisecond=789,
                    timezone=Timezone(),
                )
            )
        )


def test_echo_timestamp_value_rejects_timestamp_with_millisecond_too_high(
    basicdatatypestest_stub,
):
    """BasicDataTypesTest.EchoTimestampValue should fail with a Validation Error when provided with millisecond > 999."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=2022,
                    month=8,
                    day=5,
                    hour=12,
                    minute=34,
                    second=56,
                    millisecond=1000,
                    timezone=Timezone(),
                )
            )
        )



def test_echo_timestamp_value_accepts_minimum_timezone(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimestampValue should accept the maximum UTC offset of -14 hours."""
    response = basicdatatypestest_stub.EchoTimestampValue(
        EchoTimestampValue_Parameters(
            TimestampValue=Timestamp(
                year=2022,
                month=8,
                day=5,
                hour=12,
                minute=34,
                second=56,
                millisecond=789,
                timezone=Timezone(hours=-14)),
        )
    )
    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue == Timestamp(
        year=2022,
        month=8,
        day=5,
        hour=12,
        minute=34,
        second=56,
        millisecond=789,
        timezone=Timezone(hours=-14),
    )


def test_echo_timestamp_value_accepts_maximum_timezone(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimestampValue should accept the maximum UTC offset of 14 hours."""
    response = basicdatatypestest_stub.EchoTimestampValue(
        EchoTimestampValue_Parameters(
            TimestampValue=Timestamp(
                year=2022,
                month=8,
                day=5,
                hour=12,
                minute=34,
                second=56,
                millisecond=789,
                timezone=Timezone(hours=14),
            )
        )
    )
    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue == Timestamp(
        year=2022,
        month=8,
        day=5,
        hour=12,
        minute=34,
        second=56,
        millisecond=789,
        timezone=Timezone(hours=14),
    )


def test_echo_timestamp_value_rejects_timezones_below_minimum(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimestampValue should reject timezones below the minimum UTC offset of -14 hours."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=2022,
                    month=8,
                    day=5,
                    hour=12,
                    minute=34,
                    second=56,
                    millisecond=789,
                    timezone=Timezone(hours=-15, minutes=59),
                )
            )
        )


def test_echo_timestamp_value_rejects_timezones_above_maximum(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimestampValue should reject timezones above the maximum UTC offset of 14 hours."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=2022,
                    month=8,
                    day=5,
                    hour=12,
                    minute=34,
                    second=56,
                    millisecond=789,
                    timezone=Timezone(hours=14, minutes=1),
                )
            )
        )


def test_echo_timestamp_value_accepts_negative_timezones_with_half_hour(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimestampValue should accept timezones with a negative UTC offset and non-full hours (e.g. -13:30)."""
    response = basicdatatypestest_stub.EchoTimestampValue(
        EchoTimestampValue_Parameters(
            TimestampValue=Timestamp(
                    year=2022,
                    month=8,
                    day=5,
                    hour=12,
                    minute=34,
                    second=56,
                    millisecond=789,
                timezone=Timezone(hours=-14, minutes=30),
            )
        )
    )
    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue== Timestamp(
        year=2022,
        month=8,
        day=5,
        hour=12,
        minute=34,
        second=56,
        millisecond=789,
        timezone=Timezone(hours=-14, minutes=30),
    )


def test_echo_timestamp_value_rejects_unnormalized_timezones(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimestampValue should reject timezones where hours and minutes are not normalized."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=2022,
                    month=8,
                    day=5,
                    hour=12,
                    minute=34,
                    second=56,
                    millisecond=789,
                    timezone=Timezone(hours=0, minutes=60),
                )
            )
        )


def test_echo_timestamp_value_rejects_missing_timezone_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimestampValue should fail with a Validation Error when not provided with a timezone message."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue"
    ):
        basicdatatypestest_stub.EchoTimestampValue(
            EchoTimestampValue_Parameters(
                TimestampValue=Timestamp(
                    year=2022,
                    month=8,
                    day=5,
                    hour=12,
                    minute=34,
                    second=56,
                    millisecond=789,
                )
            )
        )


def test_echo_timestamp_value_accepts_empty_timezone_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimestampValue should work when provided with an empty timezone message."""
    response = basicdatatypestest_stub.EchoTimestampValue(
        EchoTimestampValue_Parameters(
            TimestampValue=Timestamp(
                year=2022,
                month=8,
                day=5,
                hour=12,
                minute=34,
                second=56,
                millisecond=789,
                timezone=Timezone(),
            )
        )
    )

    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue == Timestamp(
        year=2022,
        month=8,
        day=5,
        hour=12,
        minute=34,
        second=56,
        millisecond=789,
        timezone=Timezone(hours=0, minutes=0),
    )



@pytest.mark.parametrize(
    "year,month,day,hour,minute,second,millisecond,timezone_hours,timezone_minutes",
    [
        pytest.param(1, 1, 1, 0, 0, 0, 0, 0, 0, id="0001-01-01T00:00:00.000+00:00"),
        pytest.param(9999, 12, 31, 23, 59, 59, 999, 0, 0, id="9999-12-31T23:59:59.999+00:00"),
        pytest.param(2022, 8, 5, 12, 34, 56, 789, 2, 0, id="2022-08-05T12:34:56.789+02:00"),
    ],
)
def test_echo_timestamp_value(
    basicdatatypestest_stub,
    year,
    month,
    day,
    hour,
    minute,
    second,
    millisecond,
    timezone_hours,
    timezone_minutes,
):
    """BasicDataTypesTest.EchoTimestampValue should work when provided with a Timestamp message."""
    response = basicdatatypestest_stub.EchoTimestampValue(
        EchoTimestampValue_Parameters(
            TimestampValue=Timestamp(
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                second=second,
                millisecond=millisecond,
                timezone=Timezone(hours=timezone_hours, minutes=timezone_minutes),
            )
        )
    )

    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue.year == year
    assert response.ReceivedValue.month == month
    assert response.ReceivedValue.day == day
    assert response.ReceivedValue.hour == hour
    assert response.ReceivedValue.minute == minute
    assert response.ReceivedValue.second == second
    assert response.ReceivedValue.millisecond == millisecond
    assert response.ReceivedValue.timezone.hours == timezone_hours
    assert response.ReceivedValue.timezone.minutes == timezone_minutes


def test_read_timestamp_value(basicdatatypestest_stub):
    """
    BasicDataTypesTest.Get_TimestampValue with an empty parameters message should return a message containing
    the timestamp `value` 12:34:56.789, timezone +2.
    """
    response = basicdatatypestest_stub.Get_TimestampValue(
        Get_TimestampValue_Parameters()
    )
    assert response.HasField("TimestampValue")
    assert response.TimestampValue.year == 2022
    assert response.TimestampValue.month == 8
    assert response.TimestampValue.day == 5
    assert response.TimestampValue.hour == 12
    assert response.TimestampValue.minute == 34
    assert response.TimestampValue.second == 56
    assert response.TimestampValue.millisecond == 789
    assert response.TimestampValue.timezone.hours == 2
    assert response.TimestampValue.timezone.minutes == 0
