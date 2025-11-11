import math

from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import (
    Binary,
    Boolean,
    Date,
    Integer,
    Real,
    String,
    Time,
    Timestamp,
    Timezone,
)
from sila2_interop_communication_tester.helpers.fdl_tools import compare_xml


def test_set_any_type_string_value_called_with_void_type(
    server_calls,
):
    calls = server_calls["AnyTypeTest.SetAnyTypeValue"]
    assert any(
        compare_xml(
            call.request.AnyTypeValue.type,
            "<DataType><Constrained><DataType><Basic>String</Basic></DataType><Constraints><Length>0</Length></Constraints></Constrained></DataType>",
        )
        and call.request.AnyTypeValue.payload == b""
        for call in calls
    )


def test_set_any_type_string_value_called_with_sila2_any_type_of_string_type(
    server_calls,
):
    calls = server_calls["AnyTypeTest.SetAnyTypeValue"]
    assert any(
        compare_xml(
            call.request.AnyTypeValue.type, "<DataType><Basic>String</Basic></DataType>"
        )
        and call.request.AnyTypeValue.payload == (
            b"\x0a\x1e"  # field 1: 30 bytes
            + String(value="SiLA_Any_type_of_String_type").SerializeToString()
        )
        for call in calls
    )


def test_set_any_type_integer_value_called_with_any_type_integer_value_5124(
    server_calls,
):
    calls = server_calls["AnyTypeTest.SetAnyTypeValue"]
    assert any(
        compare_xml(
            call.request.AnyTypeValue.type,
            "<DataType><Basic>Integer</Basic></DataType>",
        )
        and call.request.AnyTypeValue.payload == (
            b"\x0a\x03"  # field 1: 3 bytes
            + Integer(value=5124).SerializeToString()
        )
        for call in calls
    )


def test_set_any_type_real_value_called_with_any_type_real_value_3_1415926(
    server_calls,
):
    calls = server_calls["AnyTypeTest.SetAnyTypeValue"]
    assert any(
        compare_xml(
            call.request.AnyTypeValue.type, "<DataType><Basic>Real</Basic></DataType>"
        )
        and len(call.request.AnyTypeValue.payload) == 11
        and call.request.AnyTypeValue.payload.startswith(b"\x0a\x09")  # field 1: 9 bytes
        and math.isclose(
            Real.FromString(call.request.AnyTypeValue.payload[2:]).value, 3.1415926
        )
        for call in calls
    )


def test_set_any_type_boolean_value_called_with_any_type_boolean_value_true(
    server_calls,
):
    calls = server_calls["AnyTypeTest.SetAnyTypeValue"]
    assert any(
        compare_xml(
            call.request.AnyTypeValue.type,
            "<DataType><Basic>Boolean</Basic></DataType>",
        )
        and call.request.AnyTypeValue.payload == (
            b"\x0a\x02"  # field 1: 2 bytes
            + Boolean(value=True).SerializeToString()
        )
        for call in calls
    )


def test_set_any_type_binary_value_called_with_sila2_any_type_of_binary_type(
    server_calls,
):
    calls = server_calls["AnyTypeTest.SetAnyTypeValue"]
    assert any(
        compare_xml(
            call.request.AnyTypeValue.type, "<DataType><Basic>Binary</Basic></DataType>"
        )
        and call.request.AnyTypeValue.payload == (
            b"\x0a\x1e"  # field 1: 30 bytes
            + Binary(value=b"SiLA_Any_type_of_Binary_type").SerializeToString()
        )
        for call in calls
    )


def test_set_any_type_date_value_called_with_any_type_date_value_2022_8_5_2_0(
    server_calls,
):
    calls = server_calls["AnyTypeTest.SetAnyTypeValue"]
    assert any(
        compare_xml(
            call.request.AnyTypeValue.type, "<DataType><Basic>Date</Basic></DataType>"
        )
        and call.request.AnyTypeValue.payload == (
            b"\x0a\x0b"  # field 1: 11 bytes
            + Date(year=2022, month=8, day=5, timezone=Timezone(hours=2)).SerializeToString()
        )
        for call in calls
    )


def test_set_any_type_time_value_called_with_any_type_time_value_12_34_56_2_0(
    server_calls,
):
    calls = server_calls["AnyTypeTest.SetAnyTypeValue"]
    assert any(
        compare_xml(
            call.request.AnyTypeValue.type, "<DataType><Basic>Time</Basic></DataType>"
        )
        and call.request.AnyTypeValue.payload == (
            b"\x0a\x0d"  # field 1: 13 bytes
            + Time(
                hour=12,
                minute=34,
                second=56,
                millisecond=789,
                timezone=Timezone(hours=2),
            ).SerializeToString()
        )
        for call in calls
    )


def test_set_any_type_timestamp_value_called_with_any_type_timestamp_value_2022_8_5_12_34_56_2_0(
    server_calls,
):
    calls = server_calls["AnyTypeTest.SetAnyTypeValue"]
    assert any(
        compare_xml(
            call.request.AnyTypeValue.type,
            "<DataType><Basic>Timestamp</Basic></DataType>",
        )
        and call.request.AnyTypeValue.payload == (
            b"\x0a\x14"  # field 1: 20 bytes
            + Timestamp(
                year=2022,
                month=8,
                day=5,
                hour=12,
                minute=34,
                second=56,
                millisecond=789,
                timezone=Timezone(hours=2),
            ).SerializeToString()
        )
        for call in calls
    )


def test_set_any_type_list_value_called_with_sila_2_any_type_string_list(
    server_calls,
):
    calls = server_calls["AnyTypeTest.SetAnyTypeValue"]
    assert any(
        compare_xml(
            call.request.AnyTypeValue.type,
            "<DataType><List><DataType><Basic>String</Basic></DataType></List></DataType>",
        )
        and call.request.AnyTypeValue.payload == (
            b"\x0a\x08"  # field 1: embedded message of length 8
            + String(value="SiLA 2").SerializeToString()
            + b"\x0a\x05"  # field 1: embedded message of length 6
            + String(value="Any").SerializeToString()
            + b"\x0a\x06"  # field 1: embedded message of length 6
            + String(value="Type").SerializeToString()
            + b"\x0a\x08"  # field 1: embedded message of length 8
            + String(value="String").SerializeToString()
            + b"\x0a\x06"  # field 1: embedded message of length 6
            + String(value="List").SerializeToString()
        )
        for call in calls
    )


def test_set_any_type_list_value_called_with_any_type_structure_value(
    server_calls,
):
    calls = server_calls["AnyTypeTest.SetAnyTypeValue"]
    assert any(
        compare_xml(
            call.request.AnyTypeValue.type,
            """
            <DataType>
                <Structure>
                    <Element>
                        <Identifier>StringTypeValue</Identifier>
                        <DisplayName>String Type Value</DisplayName>
                        <Description>A string value.</Description>
                        <DataType>
                            <Basic>String</Basic>
                        </DataType>
                    </Element>
                    <Element>
                        <Identifier>IntegerTypeValue</Identifier>
                        <DisplayName>Integer Type Value</DisplayName>
                        <Description>An integer value.</Description>
                        <DataType>
                            <Basic>Integer</Basic>
                        </DataType>
                    </Element>
                    <Element>
                        <Identifier>DateTypeValue</Identifier>
                        <DisplayName>Date Type Value</DisplayName>
                        <Description>A date value.</Description>
                        <DataType>
                            <Basic>Date</Basic>
                        </DataType>
                    </Element>
                </Structure>
            </DataType>
        """.replace(" ", "").replace("\n", ""),
        )
        and call.request.AnyTypeValue.payload == (
            b"\x0a\x26"  # outer message: embedded message - 38 bytes (0x26)
            + b"\x0a\x10"  # element 1: embedded message - 16 bytes (0x10)
            + b"\x0a\x0e"  # value of element 1: String of length 14 (0x0e)
            + b"A String value"
            + b"\x12\x05"  # element 2: embedded message - 5 bytes (0x05)
            + Integer(value=83737665).SerializeToString()
            + b"\x1a\x0b"  # element 3: embedded message - 11 bytes(0x0b)
            + Date(year=2022, month=8, day=5, timezone=Timezone(hours=2)).SerializeToString()
        )
        for call in calls
    )


def test_any_type_string_value_requested(server_calls):
    calls = server_calls["AnyTypeTest.Get_AnyTypeStringValue"]
    assert any(call.successful for call in calls)


def test_any_type_integer_value_requested(server_calls):
    calls = server_calls["AnyTypeTest.Get_AnyTypeIntegerValue"]
    assert any(call.successful for call in calls)


def test_any_type_real_value_requested(server_calls):
    calls = server_calls["AnyTypeTest.Get_AnyTypeRealValue"]
    assert any(call.successful for call in calls)


def test_any_type_binary_value_requested(server_calls):
    calls = server_calls["AnyTypeTest.Get_AnyTypeBinaryValue"]
    assert any(call.successful for call in calls)


def test_any_type_boolean_value_requested(server_calls):
    calls = server_calls["AnyTypeTest.Get_AnyTypeBooleanValue"]
    assert any(call.successful for call in calls)


def test_any_type_date_value_requested(server_calls):
    calls = server_calls["AnyTypeTest.Get_AnyTypeDateValue"]
    assert any(call.successful for call in calls)


def test_any_type_time_value_requested(server_calls):
    calls = server_calls["AnyTypeTest.Get_AnyTypeTimeValue"]
    assert any(call.successful for call in calls)


def test_any_type_timestamp_value_requested(server_calls):
    calls = server_calls["AnyTypeTest.Get_AnyTypeTimestampValue"]
    assert any(call.successful for call in calls)


def test_any_type_list_value_requested(server_calls):
    calls = server_calls["AnyTypeTest.Get_AnyTypeListValue"]
    assert any(call.successful for call in calls)


def test_any_type_structure_value_requested(server_calls):
    calls = server_calls["AnyTypeTest.Get_AnyTypeStructureValue"]
    assert any(call.successful for call in calls)
