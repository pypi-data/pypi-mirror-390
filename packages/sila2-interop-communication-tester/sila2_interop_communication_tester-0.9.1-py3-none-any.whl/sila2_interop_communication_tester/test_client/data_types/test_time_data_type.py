import pytest

from sila2_interop_communication_tester.grpc_stubs.BasicDataTypesTest_pb2 import (
    EchoTimeValue_Parameters,
    Get_TimeValue_Parameters,
)
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import (
    Time,
    Timezone,
)
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_validation_error,
)


def test_echo_time_value_rejects_empty_parameter_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimeValue should fail with a Validation Error if the parameter message was empty."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue"
    ):
        basicdatatypestest_stub.EchoTimeValue(EchoTimeValue_Parameters())


def test_echo_time_value_rejects_time_with_hour_too_high(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimeValue should fail with a Validation Error when provided with hour > 23."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue"
    ):
        basicdatatypestest_stub.EchoTimeValue(
            EchoTimeValue_Parameters(
                TimeValue=Time(hour=24, minute=34, second=56, millisecond=789, timezone=Timezone())
            )
        )


def test_echo_time_value_rejects_time_with_minute_too_high(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimeValue should fail with a Validation Error when provided with minute > 59."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue"
    ):
        basicdatatypestest_stub.EchoTimeValue(
            EchoTimeValue_Parameters(
                TimeValue=Time(hour=12, minute=60, second=56, millisecond=789, timezone=Timezone())
            )
        )


def test_echo_time_value_rejects_time_with_second_too_high(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimeValue should fail with a Validation Error when provided with second > 59."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue"
    ):
        basicdatatypestest_stub.EchoTimeValue(
            EchoTimeValue_Parameters(
                TimeValue=Time(hour=12, minute=34, second=60, millisecond=789, timezone=Timezone())
            )
        )


def test_echo_time_value_rejects_time_with_millisecond_too_high(
    basicdatatypestest_stub,
):
    """BasicDataTypesTest.EchoTimeValue should fail with a Validation Error when provided with millisecond > 999."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue"
    ):
        basicdatatypestest_stub.EchoTimeValue(
            EchoTimeValue_Parameters(
                TimeValue=Time(hour=12, minute=34, second=56, millisecond=1000, timezone=Timezone())
            )
        )


def test_echo_time_value_accepts_minimum_timezone(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimeValue should accept the maximum UTC offset of -14 hours."""
    response = basicdatatypestest_stub.EchoTimeValue(
        EchoTimeValue_Parameters(
            TimeValue=Time(hour=12, minute=34, second=56, millisecond=789, timezone=Timezone(hours=-14))
        )
    )
    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue == Time(hour=12, minute=34, second=56, millisecond=789, timezone=Timezone(hours=-14))


def test_echo_time_value_accepts_maximum_timezone(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimeValue should accept the maximum UTC offset of 14 hours."""
    response = basicdatatypestest_stub.EchoTimeValue(
        EchoTimeValue_Parameters(
            TimeValue=Time(hour=12, minute=34, second=56, millisecond=789, timezone=Timezone(hours=14))
        )
    )
    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue == Time(hour=12, minute=34, second=56, millisecond=789, timezone=Timezone(hours=14))


def test_echo_time_value_rejects_timezones_below_minimum(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimeValue should reject timezones below the minimum UTC offset of -14 hours."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue"
    ):
        basicdatatypestest_stub.EchoTimeValue(
            EchoTimeValue_Parameters(
                TimeValue=Time(hour=12, minute=34, second=56, millisecond=789, timezone=Timezone(hours=-15, minutes=59))
            )
        )


def test_echo_time_value_rejects_timezones_above_maximum(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimeValue should reject timezones above the maximum UTC offset of 14 hours."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue"
    ):
        basicdatatypestest_stub.EchoTimeValue(
            EchoTimeValue_Parameters(
                TimeValue=Time(hour=12, minute=34, second=56, millisecond=789, timezone=Timezone(hours=14, minutes=1))
            )
        )


def test_echo_time_value_accepts_negative_timezones_with_half_hour(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimeValue should accept timezones with a negative UTC offset and non-full hours (e.g. -13:30)."""
    response = basicdatatypestest_stub.EchoTimeValue(
        EchoTimeValue_Parameters(
            TimeValue=Time(hour=12, minute=34, second=56, millisecond=789, timezone=Timezone(hours=-14, minutes=30))
        )
    )
    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue== Time(hour=12, minute=34, second=56, millisecond=789, timezone=Timezone(hours=-14, minutes=30))


def test_echo_time_value_rejects_unnormalized_timezones(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimeValue should reject timezones where hours and minutes are not normalized."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue"
    ):
        basicdatatypestest_stub.EchoTimeValue(
            EchoTimeValue_Parameters(
                TimeValue=Time(hour=12, minute=34, second=56, millisecond=789, timezone=Timezone(hours=0, minutes=60))
            )
        )


def test_echo_time_value_rejects_missing_timezone_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimeValue should fail with a Validation Error when not provided with a timezone message."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue"
    ):
        basicdatatypestest_stub.EchoTimeValue(
            EchoTimeValue_Parameters(TimeValue=Time(hour=12, minute=34, second=56, millisecond=789))
        )


def test_echo_time_value_accepts_empty_timezone_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoTimeValue should work when provided with an empty timezone message."""
    response = basicdatatypestest_stub.EchoTimeValue(
        EchoTimeValue_Parameters(
            TimeValue=Time(hour=12, minute=34, second=56, millisecond=789, timezone=Timezone())
        )
    )

    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue == Time(hour=12, minute=34, second=56, millisecond=789, timezone=Timezone(hours=0, minutes=0))


@pytest.mark.parametrize(
    "hour,minute,second,millisecond,timezone_hours,timezone_minutes",
    [(0, 0, 0, 0, 0, 0), (12, 34, 56, 789, 2, 0), (23, 59, 59, 999, 0, 0)],
)
def test_echo_time_value(
    basicdatatypestest_stub,
    hour,
    minute,
    second,
    millisecond,
    timezone_hours,
    timezone_minutes,
):
    """BasicDataTypesTest.EchoTimeValue should work when provided with a Time message."""
    response = basicdatatypestest_stub.EchoTimeValue(
        EchoTimeValue_Parameters(
            TimeValue=Time(
                hour=hour,
                minute=minute,
                second=second,
                millisecond=millisecond,
                timezone=Timezone(hours=timezone_hours, minutes=timezone_minutes),
            )
        )
    )

    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue.hour == hour
    assert response.ReceivedValue.minute == minute
    assert response.ReceivedValue.second == second
    assert response.ReceivedValue.millisecond == millisecond
    assert response.ReceivedValue.timezone.hours == timezone_hours
    assert response.ReceivedValue.timezone.minutes == timezone_minutes


def test_read_time_value(basicdatatypestest_stub):
    """
    BasicDataTypesTest.Get_TimeValue with an empty parameters message should return a message containing
    the time `value` 12:34:56.789, timezone +2.
    """
    response = basicdatatypestest_stub.Get_TimeValue(Get_TimeValue_Parameters())
    assert response.HasField("TimeValue")
    assert response.TimeValue.hour == 12
    assert response.TimeValue.minute == 34
    assert response.TimeValue.second == 56
    assert response.TimeValue.millisecond == 789
    assert response.TimeValue.timezone.hours == 2
    assert response.TimeValue.timezone.minutes == 0
