import pytest

from sila2_interop_communication_tester.grpc_stubs.BasicDataTypesTest_pb2 import (
    EchoDateValue_Parameters,
    Get_DateValue_Parameters,
)
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import (
    Date,
    Timezone,
)
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_validation_error,
)


def test_echo_date_value_rejects_empty_parameter_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should fail with a Validation Error if the parameter message was empty."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue"
    ):
        basicdatatypestest_stub.EchoDateValue(EchoDateValue_Parameters())


def test_echo_date_value_rejects_empty_date_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should fail with a Validation Error when provided with an empty Date message."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue"
    ):
        basicdatatypestest_stub.EchoDateValue(
            EchoDateValue_Parameters(DateValue=Date())
        )


def test_echo_date_value_rejects_date_with_day_too_low(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should fail with a Validation Error when provided with day < 1."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue"
    ):
        basicdatatypestest_stub.EchoDateValue(
            EchoDateValue_Parameters(DateValue=Date(year=2022, month=8, day=0, timezone=Timezone()))
        )


def test_echo_date_value_rejects_date_with_day_too_high(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should fail with a Validation Error when provided with day > 31."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue"
    ):
        basicdatatypestest_stub.EchoDateValue(
            EchoDateValue_Parameters(DateValue=Date(year=2022, month=8, day=32, timezone=Timezone()))
        )


def test_echo_date_value_rejects_date_with_month_too_low(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should fail with a Validation Error when provided with month < 1."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue"
    ):
        basicdatatypestest_stub.EchoDateValue(
            EchoDateValue_Parameters(DateValue=Date(year=2022, month=0, day=5, timezone=Timezone()))
        )


def test_echo_date_value_rejects_date_with_month_too_high(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should fail with a Validation Error when provided with month > 12."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue"
    ):
        basicdatatypestest_stub.EchoDateValue(
            EchoDateValue_Parameters(DateValue=Date(year=2022, month=13, day=5, timezone=Timezone()))
        )


def test_echo_date_value_rejects_date_with_year_too_low(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should fail with a Validation Error when provided with year < 1."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue"
    ):
        basicdatatypestest_stub.EchoDateValue(
            EchoDateValue_Parameters(DateValue=Date(year=0, month=8, day=5, timezone=Timezone()))
        )


def test_echo_date_value_rejects_date_with_year_too_high(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should fail with a Validation Error when provided with year > 9999."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue"
    ):
        basicdatatypestest_stub.EchoDateValue(
            EchoDateValue_Parameters(DateValue=Date(year=10000, month=8, day=5, timezone=Timezone()))
        )


def test_echo_date_value_accepts_minimum_timezone(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should accept the maximum UTC offset of -14 hours."""
    response = basicdatatypestest_stub.EchoDateValue(
        EchoDateValue_Parameters(
            DateValue=Date(year=2022, month=8, day=5, timezone=Timezone(hours=-14))
        )
    )
    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue == Date(year=2022, month=8, day=5, timezone=Timezone(hours=-14))


def test_echo_date_value_accepts_maximum_timezone(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should accept the maximum UTC offset of 14 hours."""
    response = basicdatatypestest_stub.EchoDateValue(
        EchoDateValue_Parameters(
            DateValue=Date(year=2022, month=8, day=5, timezone=Timezone(hours=14))
        )
    )
    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue == Date(year=2022, month=8, day=5, timezone=Timezone(hours=14))


def test_echo_date_value_rejects_timezones_below_minimum(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should reject timezones below the minimum UTC offset of -14 hours."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue"
    ):
        basicdatatypestest_stub.EchoDateValue(
            EchoDateValue_Parameters(
                DateValue=Date(year=2022, month=8, day=5, timezone=Timezone(hours=-15, minutes=59))
            )
        )


def test_echo_date_value_rejects_timezones_above_maximum(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should reject timezones above the maximum UTC offset of 14 hours."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue"
    ):
        basicdatatypestest_stub.EchoDateValue(
            EchoDateValue_Parameters(
                DateValue=Date(year=2022, month=8, day=5, timezone=Timezone(hours=14, minutes=1))
            )
        )


def test_echo_date_value_accepts_negative_timezones_with_half_hour(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should accept timezones with a negative UTC offset and non-full hours (e.g. -13:30)."""
    response = basicdatatypestest_stub.EchoDateValue(
        EchoDateValue_Parameters(
            DateValue=Date(year=2022, month=8, day=5, timezone=Timezone(hours=-14, minutes=30))
        )
    )
    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue== Date(year=2022, month=8, day=5, timezone=Timezone(hours=-14, minutes=30))


def test_echo_date_value_rejects_unnormalized_timezones(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should reject timezones where hours and minutes are not normalized."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue"
    ):
        basicdatatypestest_stub.EchoDateValue(
            EchoDateValue_Parameters(
                DateValue=Date(year=2022, month=8, day=5, timezone=Timezone(hours=0, minutes=60))
            )
        )


def test_echo_date_value_rejects_missing_timezone_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should fail with a Validation Error when not provided with a timezone message."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue"
    ):
        basicdatatypestest_stub.EchoDateValue(
            EchoDateValue_Parameters(DateValue=Date(year=2022, month=8, day=5))
        )


def test_echo_date_value_accepts_empty_timezone_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoDateValue should work when provided with an empty timezone message."""
    response = basicdatatypestest_stub.EchoDateValue(
        EchoDateValue_Parameters(
            DateValue=Date(year=2022, month=8, day=5, timezone=Timezone())
        )
    )

    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue == Date(year=2022, month=8, day=5, timezone=Timezone(hours=0, minutes=0))


@pytest.mark.parametrize(
    "year,month,day,timezone_hours,timezone_minutes",
    [
        pytest.param(1, 1, 1, 0, 0, id="0001-01-01+00:00"),
        pytest.param(2022, 8, 5, 2, 0, id="2022-08-05+02:00"),
        pytest.param(9999, 12, 31, 0, 0, id="9999-12-31+00:00"),
    ],
)
def test_echo_date_value(
    basicdatatypestest_stub, year, month, day, timezone_hours, timezone_minutes
):
    """BasicDataTypesTest.EchoDateValue should work when provided with a Date message."""
    response = basicdatatypestest_stub.EchoDateValue(
        EchoDateValue_Parameters(
            DateValue=Date(
                year=year,
                month=month,
                day=day,
                timezone=Timezone(hours=timezone_hours, minutes=timezone_minutes),
            )
        )
    )

    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue.year == year
    assert response.ReceivedValue.month == month
    assert response.ReceivedValue.day == day
    assert response.ReceivedValue.timezone.hours == timezone_hours
    assert response.ReceivedValue.timezone.minutes == timezone_minutes


def test_read_date_value(basicdatatypestest_stub):
    """
    BasicDataTypesTest.Get_DateValue with an empty parameters message should return a message containing
    the date `value` 05.08.2022 respective 08/05/2018, timezone +2.
    """
    response = basicdatatypestest_stub.Get_DateValue(Get_DateValue_Parameters())
    assert response.HasField("DateValue")
    assert response.DateValue.year == 2022
    assert response.DateValue.month == 8
    assert response.DateValue.day == 5
    assert response.DateValue.timezone.hours == 2
    assert response.DateValue.timezone.minutes == 0
