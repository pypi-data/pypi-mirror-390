import math


def test_echo_string_value_called_with_sila2_test_string_value(server_calls):
    calls = server_calls["BasicDataTypesTest.EchoStringValue"]
    assert any(call.request.StringValue.value == "SiLA2_Test_String_Value" for call in calls)


def test_echo_integer_value_called_with_5124(server_calls):
    calls = server_calls["BasicDataTypesTest.EchoIntegerValue"]
    assert any(call.request.IntegerValue.value == 5124 for call in calls)


def test_echo_real_value_called_with_3_1415926(server_calls):
    calls = server_calls["BasicDataTypesTest.EchoRealValue"]
    assert any(math.isclose(call.request.RealValue.value, 3.1415926) for call in calls)


def test_echo_boolean_value_called_with_true(server_calls):
    calls = server_calls["BasicDataTypesTest.EchoBooleanValue"]
    assert any(call.request.BooleanValue.value is True for call in calls)


def test_echo_date_value_called_with_2022_8_5_2_0(server_calls):
    calls = server_calls["BasicDataTypesTest.EchoDateValue"]
    assert any(
        call.request.DateValue.year == 2022
        and call.request.DateValue.month == 8
        and call.request.DateValue.day == 5
        and call.request.DateValue.timezone.hours == 2
        and call.request.DateValue.timezone.minutes == 0
        for call in calls
    )


def test_echo_time_value_called_with_12_34_56_2_0(server_calls):
    calls = server_calls["BasicDataTypesTest.EchoTimeValue"]
    assert any(
        call.request.TimeValue.hour == 12
        and call.request.TimeValue.minute == 34
        and call.request.TimeValue.second == 56
        and call.request.TimeValue.millisecond == 789
        and call.request.TimeValue.timezone.hours == 2
        and call.request.TimeValue.timezone.minutes == 0
        for call in calls
    )


def test_echo_timestamp_value_called_with_2022_8_5_12_34_56_2_0(server_calls):
    calls = server_calls["BasicDataTypesTest.EchoTimestampValue"]
    assert any(
        call.request.TimestampValue.year == 2022
        and call.request.TimestampValue.month == 8
        and call.request.TimestampValue.day == 5
        and call.request.TimestampValue.hour == 12
        and call.request.TimestampValue.minute == 34
        and call.request.TimestampValue.second == 56
        and call.request.TimestampValue.millisecond == 789
        and call.request.TimestampValue.timezone.hours == 2
        and call.request.TimestampValue.timezone.minutes == 0
        for call in calls
    )


def test_string_value_requested(server_calls):
    calls = server_calls["BasicDataTypesTest.Get_StringValue"]
    assert any(call.successful for call in calls)


def test_integer_value_requested(server_calls):
    calls = server_calls["BasicDataTypesTest.Get_IntegerValue"]
    assert any(call.successful for call in calls)


def test_real_value_requested(server_calls):
    calls = server_calls["BasicDataTypesTest.Get_RealValue"]
    assert any(call.successful for call in calls)


def test_boolean_value_requested(server_calls):
    calls = server_calls["BasicDataTypesTest.Get_BooleanValue"]
    assert any(call.successful for call in calls)


def test_date_value_requested(server_calls):
    calls = server_calls["BasicDataTypesTest.Get_DateValue"]
    assert any(call.successful for call in calls)


def test_time_value_requested(server_calls):
    calls = server_calls["BasicDataTypesTest.Get_TimeValue"]
    assert any(call.successful for call in calls)


def test_timestamp_value_requested(server_calls):
    calls = server_calls["BasicDataTypesTest.Get_TimestampValue"]
    assert any(call.successful for call in calls)
