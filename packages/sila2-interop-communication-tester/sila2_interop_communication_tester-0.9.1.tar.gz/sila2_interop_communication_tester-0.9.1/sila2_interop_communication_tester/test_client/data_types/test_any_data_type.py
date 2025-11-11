import math

import pytest

from sila2_interop_communication_tester.grpc_stubs.AnyTypeTest_pb2 import (
    Get_AnyTypeBinaryValue_Parameters,
    Get_AnyTypeBooleanValue_Parameters,
    Get_AnyTypeDateValue_Parameters,
    Get_AnyTypeIntegerValue_Parameters,
    Get_AnyTypeListValue_Parameters,
    Get_AnyTypeRealValue_Parameters,
    Get_AnyTypeStringValue_Parameters,
    Get_AnyTypeStructureValue_Parameters,
    Get_AnyTypeTimestampValue_Parameters,
    Get_AnyTypeTimeValue_Parameters,
    SetAnyTypeValue_Parameters,
)
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import (
    Any,
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
from sila2_interop_communication_tester.helpers.protobuf_helpers import create_any_message


def test_set_any_type_value_with_void_message(anytypetest_stub):
    """AnyTypeTest.SetAnyTypeValue should work when provided with a Void message."""
    void = "<DataType><Constrained><DataType><Basic>String</Basic></DataType><Constraints><Length>0</Length></Constraints></Constrained></DataType>"
    response = anytypetest_stub.SetAnyTypeValue(
        SetAnyTypeValue_Parameters(AnyTypeValue=Any(type=void, payload=b""))
    )

    assert response.HasField("ReceivedAnyType")
    assert compare_xml(response.ReceivedAnyType.value, void)
    assert compare_xml(response.ReceivedValue.type, void)
    assert response.ReceivedValue.payload == b""  # field 1: 0 bytes


@pytest.mark.parametrize(
    "type_xml,message",
    [
        pytest.param(
            "<DataType><Basic>String</Basic></DataType>",
            String(value="SiLA_Any_type_of_String_type"),
            id="String",
        ),
        pytest.param(
            "<DataType><Basic>Integer</Basic></DataType>",
            Integer(value=5124),
            id="Integer",
        ),
        pytest.param(
            "<DataType><Basic>Real</Basic></DataType>",
            Real(value=3.1415926),
            id="Real",
        ),
        pytest.param(
            "<DataType><Basic>Boolean</Basic></DataType>",
            Boolean(value=True),
            id="Boolean",
        ),
        pytest.param(
            "<DataType><Basic>Binary</Basic></DataType>",
            Binary(value=b"SiLA_Any_type_of_Binary_type"),
            id="Binary",
        ),
        pytest.param(
            "<DataType><Basic>Date</Basic></DataType>",
            Date(year=2022, month=8, day=5, timezone=Timezone(hours=2)),
            id="Date",
        ),
        pytest.param(
            "<DataType><Basic>Time</Basic></DataType>",
            Time(
                hour=12,
                minute=34,
                second=56,
                millisecond=789,
                timezone=Timezone(hours=2),
            ),
            id="Time",
        ),
        pytest.param(
            "<DataType><Basic>Timestamp</Basic></DataType>",
            Timestamp(
                year=2022,
                month=8,
                day=5,
                hour=12,
                minute=34,
                second=56,
                millisecond=789,
                timezone=Timezone(hours=2),
            ),
            id="Timestamp",
        ),
    ],
)
def test_set_any_type_value_with_basic_type(anytypetest_stub, type_xml, message):
    """AnyTypeTest.SetAnyTypeValue should work when provided with an Any Type message of Basic types."""
    response = anytypetest_stub.SetAnyTypeValue(
        SetAnyTypeValue_Parameters(AnyTypeValue=create_any_message(type_xml, message))
    )

    assert response.HasField("ReceivedAnyType")
    assert compare_xml(response.ReceivedAnyType.value, type_xml)
    assert compare_xml(response.ReceivedValue.type, type_xml)
    assert response.ReceivedValue.payload == (
        b"\x0a"  # type of field 1: message
        + len(message.SerializeToString()).to_bytes(1, byteorder="big")
        + message.SerializeToString()  # embedded message
    )


def test_set_any_type_value_with_list(anytypetest_stub):
    """AnyTypeTest.SetAnyTypeValue should work when provided with an Any Type message of List types."""
    type_xml = "<DataType><List><DataType><Basic>String</Basic></DataType></List></DataType>"
    response = anytypetest_stub.SetAnyTypeValue(
        SetAnyTypeValue_Parameters(
            AnyTypeValue=create_any_message(
                type_xml,
                [
                    String(value="SiLA 2"),
                    String(value="Any"),
                    String(value="Type"),
                    String(value="String"),
                    String(value="List"),
                ],
            )
        )
    )

    assert response.HasField("ReceivedAnyType")
    assert compare_xml(response.ReceivedAnyType.value, type_xml)
    assert compare_xml(response.ReceivedValue.type, type_xml)
    assert response.ReceivedValue.payload == (
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


def test_set_any_type_value_with_structure(anytypetest_stub):
    """AnyTypeTest.SetAnyTypeValue should work when provided with an Any Type message of Structure types."""
    type_xml = """
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
    """.replace(" ", "").replace("\n", "")

    request_message = Any(
        type=type_xml,
        payload=(
            b"\x0a\x26"  # outer message: embedded message - 38 bytes (0x26)
            + b"\x0a\x10"  # element 1: embedded message - 16 bytes (0x10)
            + b"\x0a\x0e"  # value of element 1: String of length 14 (0x0e)
            + b"A String value"
            + b"\x12\x05"  # element 2: embedded message - 5 bytes (0x05)
            + Integer(value=83737665).SerializeToString()
            + b"\x1a\x0b"  # element 3: embedded message - 11 bytes(0x0b)
            + Date(year=2022, month=8, day=5, timezone=Timezone(hours=2)).SerializeToString()
        ),
    )
    response = anytypetest_stub.SetAnyTypeValue(
        SetAnyTypeValue_Parameters(AnyTypeValue=request_message)
    )

    assert response.HasField("ReceivedAnyType")
    assert compare_xml(response.ReceivedAnyType.value, type_xml)
    assert compare_xml(response.ReceivedValue.type, type_xml)
    assert response.ReceivedValue.payload == request_message.payload

def test_read_any_type_string_value(anytypetest_stub):
    """
    AnyTypeTest.Get_AnyTypeStringValue with an empty parameters message should return a message containing
    the Any type String value 'SiLA_Any_type_of_String_type'.
    """
    response = anytypetest_stub.Get_AnyTypeStringValue(Get_AnyTypeStringValue_Parameters())
    assert response.HasField("AnyTypeStringValue")
    assert compare_xml(
        response.AnyTypeStringValue.type, "<DataType><Basic>String</Basic></DataType>"
    )

    expected_embedded_message = String(value="SiLA_Any_type_of_String_type").SerializeToString()
    assert response.AnyTypeStringValue.payload == (
        b"\x0a"  # type of field 1: message
        + len(expected_embedded_message).to_bytes(1, byteorder="big")
        + expected_embedded_message
    )


def test_read_any_type_integer_value(anytypetest_stub):
    """
    AnyTypeTest.Get_AnyTypeIntegerValue with an empty parameters message should return a message containing
    the Any type Integer value 5124.
    """
    response = anytypetest_stub.Get_AnyTypeIntegerValue(Get_AnyTypeIntegerValue_Parameters())
    assert response.HasField("AnyTypeIntegerValue")
    assert compare_xml(
        response.AnyTypeIntegerValue.type, "<DataType><Basic>Integer</Basic></DataType>"
    )

    expected_embedded_message = Integer(value=5124).SerializeToString()
    assert response.AnyTypeIntegerValue.payload == (
        b"\x0a"  # type of field 1: message
        + len(expected_embedded_message).to_bytes(1, byteorder="big")
        + expected_embedded_message
    )


def test_read_any_type_real_value(anytypetest_stub):
    """
    AnyTypeTest.Get_AnyTypeRealValue with an empty parameters message should return a message containing
    the Any type Real value 3.1415926.
    """
    response = anytypetest_stub.Get_AnyTypeRealValue(Get_AnyTypeRealValue_Parameters())
    assert response.HasField("AnyTypeRealValue")
    assert compare_xml(
        response.AnyTypeRealValue.type, "<DataType><Basic>Real</Basic></DataType>"
    )

    assert response.AnyTypeRealValue.payload.startswith(
        b"\x0a"  # type of field 1: message
        + b"\x09"  # length of embedded message: 1 byte for the Real message, 8 bytes for float64
    )
    embedded_message = Real.FromString(response.AnyTypeRealValue.payload[2:])
    assert math.isclose(embedded_message.value, 3.1415926)


def test_read_any_type_boolean_value(anytypetest_stub):
    """
    AnyTypeTest.Get_AnyTypeBooleanValue with an empty parameters message should return a message containing
    the Any type Boolean value true.
    """
    response = anytypetest_stub.Get_AnyTypeBooleanValue(Get_AnyTypeBooleanValue_Parameters())
    assert response.HasField("AnyTypeBooleanValue")
    assert compare_xml(
        response.AnyTypeBooleanValue.type, "<DataType><Basic>Boolean</Basic></DataType>"
    )

    expected_embedded_message = Boolean(value=True).SerializeToString()
    assert response.AnyTypeBooleanValue.payload == (
        b"\x0a"  # type of field 1: message
        + len(expected_embedded_message).to_bytes(1, byteorder="big")
        + expected_embedded_message
    )


def test_read_any_type_binary_value(anytypetest_stub):
    """
    AnyTypeTest.Get_AnyTypeBinaryValue with an empty parameters message should return a message containing
    the Any type ASCII-encoded string value 'SiLA_Any_type_of_Binary_type' as Binary.
    """
    response = anytypetest_stub.Get_AnyTypeBinaryValue(Get_AnyTypeBinaryValue_Parameters())
    assert response.HasField("AnyTypeBinaryValue")
    assert compare_xml(
        response.AnyTypeBinaryValue.type, "<DataType><Basic>Binary</Basic></DataType>"
    )

    expected_embedded_message = Binary(value=b"SiLA_Any_type_of_Binary_type").SerializeToString()
    assert response.AnyTypeBinaryValue.payload == (
        b"\x0a"  # type of field 1: message
        + len(expected_embedded_message).to_bytes(1, byteorder="big")
        + expected_embedded_message
    )


def test_read_any_type_date_value(anytypetest_stub):
    """
    AnyTypeTest.Get_AnyTypeDateValue with an empty parameters message should return a message containing
    the Any type Date value 05.08.2022 respective 08/05/2022, timezone +2.
    """
    response = anytypetest_stub.Get_AnyTypeDateValue(Get_AnyTypeDateValue_Parameters())
    assert response.HasField("AnyTypeDateValue")
    assert compare_xml(
        response.AnyTypeDateValue.type, "<DataType><Basic>Date</Basic></DataType>"
    )

    expected_embedded_message = Date(year=2022, month=8, day=5, timezone=Timezone(hours=2)).SerializeToString()
    assert response.AnyTypeDateValue.payload == (
        b"\x0a"  # type of field 1: message
        + len(expected_embedded_message).to_bytes(1, byteorder="big")
        + expected_embedded_message
    )


def test_read_any_type_time_value(anytypetest_stub):
    """
    AnyTypeTest.Get_AnyTypeTimeValue with an empty parameters message should return a message containing
    the Any type Time value 12:34:56.789, timezone +2.
    """
    response = anytypetest_stub.Get_AnyTypeTimeValue(Get_AnyTypeTimeValue_Parameters())
    assert response.HasField("AnyTypeTimeValue")
    assert compare_xml(
        response.AnyTypeTimeValue.type, "<DataType><Basic>Time</Basic></DataType>"
    )

    expected_embedded_message = Time(
        hour=12,
        minute=34,
        second=56,
        millisecond=789,
        timezone=Timezone(hours=2),
    ).SerializeToString()
    assert response.AnyTypeTimeValue.payload == (
        b"\x0a"  # type of field 1: message
        + len(expected_embedded_message).to_bytes(1, byteorder="big")
        + expected_embedded_message
    )


def test_read_any_type_timestamp_value(anytypetest_stub):
    """
    AnyTypeTest.Get_AnyTypeTimestampValue with an empty parameters message should return a message containing
    the Any type Timestamp value 2022-08-05 12:34:56.789, timezone +2.
    """
    response = anytypetest_stub.Get_AnyTypeTimestampValue(Get_AnyTypeTimestampValue_Parameters())
    assert response.HasField("AnyTypeTimestampValue")
    assert compare_xml(
        response.AnyTypeTimestampValue.type,
        "<DataType><Basic>Timestamp</Basic></DataType>",
    )

    expected_embedded_message = Timestamp(
        year=2022,
        month=8,
        day=5,
        hour=12,
        minute=34,
        second=56,
        millisecond=789,
        timezone=Timezone(hours=2),
    ).SerializeToString()
    assert response.AnyTypeTimestampValue.payload == (
        b"\x0a"  # type of field 1: message
        + len(expected_embedded_message).to_bytes(1, byteorder="big")
        + expected_embedded_message
    )


def test_read_any_type_list_value(anytypetest_stub):
    """
    AnyTypeTest.Get_AnyTypeListValue with an empty parameters message should return a message containing
    the Any type String List value ('SiLA 2', 'Any', 'Type', 'String', 'List').
    """
    response = anytypetest_stub.Get_AnyTypeListValue(Get_AnyTypeListValue_Parameters())
    assert response.HasField("AnyTypeListValue")
    assert compare_xml(
        response.AnyTypeListValue.type,
        "<DataType><List><DataType><Basic>String</Basic></DataType></List></DataType>",
    )

    assert response.AnyTypeListValue.payload == (
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


def test_read_any_type_structure_value(anytypetest_stub):
    """
    AnyTypeTest.Get_AnyTypeStructureValue with an empty parameters message should return a message containing
    the following Any type Structure value:
      - String 'StringTypeValue' = 'A String value',
      - Integer 'IntegerTypeValue' = 83737665,
      - Date 'DateTypeValue' = 05.08.2022 respective 08/05/2022 timezone +2)
    """
    response = anytypetest_stub.Get_AnyTypeStructureValue(Get_AnyTypeStructureValue_Parameters())
    assert response.HasField("AnyTypeStructureValue")
    assert compare_xml(
        response.AnyTypeStructureValue.type,
        (
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
            """.replace(" ", "").replace("\n", "")
        ),
    )
    assert (
        response.AnyTypeStructureValue.payload == (
            b"\x0a\x26"  # outer message: embedded message - 38 bytes (0x26)
            + b"\x0a\x10"  # element 1: embedded message - 16 bytes (0x10)
            + b"\x0a\x0e"  # value of element 1: String of length 14 (0x0e)
            + b"A String value"
            + b"\x12\x05"  # element 2: embedded message - 5 bytes (0x05)
            + Integer(value=83737665).SerializeToString()
            + b"\x1a\x0b"  # element 3: embedded message - 11 bytes(0x0b)
            + Date(year=2022, month=8, day=5, timezone=Timezone(hours=2)).SerializeToString()
        )
    )
