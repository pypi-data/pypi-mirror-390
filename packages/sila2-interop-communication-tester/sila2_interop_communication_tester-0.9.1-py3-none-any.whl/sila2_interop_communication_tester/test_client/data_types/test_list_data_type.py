import pytest
import math

from sila2_interop_communication_tester.grpc_stubs.ListDataTypeTest_pb2 import (
    DataType_TestStructure,
    EchoIntegerList_Parameters,
    EchoStringList_Parameters,
    EchoStructureList_Parameters,
    Get_EmptyStringList_Parameters,
    Get_IntegerList_Parameters,
    Get_StringList_Parameters,
    Get_StructureList_Parameters,
)
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
from sila2_interop_communication_tester.helpers.protobuf_helpers import (
    create_any_message,
)
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_validation_error,
)


def test_read_empty_string_list(listdatatypetest_stub):
    """
    ListDataTypeTest.Get_EmptyStringList with an empty parameters message should return a message containing an empty
    list of String type.
    """
    response = listdatatypetest_stub.Get_EmptyStringList(
        Get_EmptyStringList_Parameters()
    )
    assert response.EmptyStringList == []


def test_echo_string_list_rejects_large_string(listdatatypetest_stub):
    """
    ListDataTypeTest.EchoStringList should fail with a Validation Error when provided with a string larger than 2**21
    characters.
    """
    with raises_validation_error(
        "org.silastandard/test/ListDataTypeTest/v1/Command/EchoStringList/Parameter/StringList"
    ):
        listdatatypetest_stub.EchoStringList(
            EchoStringList_Parameters(
                StringList=[
                    String(value="a"),
                    String(value="b"),
                    String(value="c" * (2**21 + 1)),
                ]
            )
        )


def test_echo_string_list_with_empty_string_message(listdatatypetest_stub):
    """ListDataTypeTest.EchoStringList should work when provided with an empty String message."""
    response = listdatatypetest_stub.EchoStringList(
        EchoStringList_Parameters(
            StringList=[String(value="a"), String(), String(value="c")]
        )
    )

    assert response.ReceivedValues == [String(value="a"), String(), String(value="c")]


@pytest.mark.parametrize(
    "values",
    [
        ["", "", ""],
        ["SiLA 2", "is", "great"],
    ],
    ids=repr,
)
def test_echo_string_list(listdatatypetest_stub, values):
    """ListDataTypeTest.EchoStringList should work when provided with a list of String messages."""
    response = listdatatypetest_stub.EchoStringList(
        EchoStringList_Parameters(StringList=[String(value=value) for value in values])
    )

    assert response.ReceivedValues == [String(value=value) for value in values]


def test_read_string_list(listdatatypetest_stub):
    """
    ListDataTypeTest.EchoStringList with an empty parameters message should return a message containing
    a list with the following String values: 'SiLA 2', 'is', 'great'.
    """
    response = listdatatypetest_stub.Get_StringList(Get_StringList_Parameters())
    assert response.StringList == [
        String(value="SiLA 2"),
        String(value="is"),
        String(value="great"),
    ]


def test_echo_integer_list_with_empty_integer_message(listdatatypetest_stub):
    """ListDataTypeTest.EchoIntegerList should work when provided with an empty Integer message."""
    response = listdatatypetest_stub.EchoIntegerList(
        EchoIntegerList_Parameters(
            IntegerList=[Integer(value=0), Integer(), Integer(value=1)]
        )
    )

    assert response.ReceivedValues == [Integer(value=0), Integer(), Integer(value=1)]


@pytest.mark.parametrize(
    "values",
    [
        [0, 0, 0],
        [1, 2, 3],
        [-1, -2, -3],
    ],
    ids=repr,
)
def test_echo_integer_list(listdatatypetest_stub, values):
    """ListDataTypeTest.EchoIntegerList should work when provided with a list of Integer messages."""
    response = listdatatypetest_stub.EchoIntegerList(
        EchoIntegerList_Parameters(
            IntegerList=[Integer(value=value) for value in values]
        )
    )

    assert response.ReceivedValues == [Integer(value=value) for value in values]


def test_read_integer_list(listdatatypetest_stub):
    """
    ListDataTypeTest.EchoIntegerList with an empty parameters message should return a message containing
    a list with the following Integer values: 1, 2, 3.
    """
    response = listdatatypetest_stub.Get_IntegerList(Get_IntegerList_Parameters())
    assert response.IntegerList == [
        Integer(value=1),
        Integer(value=2),
        Integer(value=3),
    ]


@pytest.mark.parametrize(
    "values",
    [
        pytest.param(
            [
                ("", 0, 0.0, False, b"", 1, 1, 1, 0, 0, 0, 0, 0, 0, ""),
                ("", 0, 0.0, False, b"", 1, 1, 1, 0, 0, 0, 0, 0, 0, ""),
                ("", 0, 0.0, False, b"", 1, 1, 1, 0, 0, 0, 0, 0, 0, ""),
            ],
            id="default-values",
        ),
        pytest.param(
            [
                (
                    "SiLA2_Test_String_Value_1",
                    5124,
                    3.1415926,
                    True,
                    b"Binary_String_Value_1",
                    2022,
                    8,
                    5,
                    12,
                    34,
                    56,
                    789,
                    2,
                    0,
                    "Any_Type_String_Value_1",
                ),
                (
                    "SiLA2_Test_String_Value_2",
                    5125,
                    4.1415926,
                    False,
                    b"Binary_String_Value_2",
                    2023,
                    9,
                    6,
                    13,
                    35,
                    57,
                    790,
                    2,
                    0,
                    "Any_Type_String_Value_2",
                ),
                (
                    "SiLA2_Test_String_Value_3",
                    5126,
                    5.1415926,
                    True,
                    b"Binary_String_Value_3",
                    2024,
                    10,
                    7,
                    14,
                    36,
                    58,
                    791,
                    2,
                    0,
                    "Any_Type_String_Value_3",
                ),
            ],
            id="custom-values",
        ),
    ],
)
def test_echo_structure_list(listdatatypetest_stub, values):
    """ListDataTypeTest.EchoStructureList should work when provided with a list of Structure messages."""
    response = listdatatypetest_stub.EchoStructureList(
        EchoStructureList_Parameters(
            StructureList=[
                DataType_TestStructure(
                    TestStructure=DataType_TestStructure.TestStructure_Struct(
                        StringTypeValue=String(value=value[0]),
                        IntegerTypeValue=Integer(value=value[1]),
                        RealTypeValue=Real(value=value[2]),
                        BooleanTypeValue=Boolean(value=value[3]),
                        BinaryTypeValue=Binary(value=value[4]),
                        DateTypeValue=Date(
                            year=value[5],
                            month=value[6],
                            day=value[7],
                            timezone=Timezone(hours=value[12], minutes=value[13]),
                        ),
                        TimeTypeValue=Time(
                            hour=value[8],
                            minute=value[9],
                            second=value[10],
                            millisecond=value[11],
                            timezone=Timezone(hours=value[12], minutes=value[13]),
                        ),
                        TimestampTypeValue=Timestamp(
                            year=value[5],
                            month=value[6],
                            day=value[7],
                            hour=value[8],
                            minute=value[9],
                            second=value[10],
                            millisecond=value[11],
                            timezone=Timezone(hours=value[12], minutes=value[13]),
                        ),
                        AnyTypeValue=create_any_message(
                            type_xml="<DataType><Basic>String</Basic></DataType>",
                            value=String(value=value[14]),
                        ),
                    )
                )
                for value in values
            ]
        )
    )

    assert len(response.ReceivedValues) == len(values)
    for item, value in zip(response.ReceivedValues, values):
        assert item.TestStructure.StringTypeValue.value == value[0]
        assert item.TestStructure.IntegerTypeValue.value == value[1]
        assert math.isclose(item.TestStructure.RealTypeValue.value, value[2])
        assert item.TestStructure.BooleanTypeValue.value == value[3]
        assert item.TestStructure.BinaryTypeValue.value == value[4]
        assert item.TestStructure.DateTypeValue.year == value[5]
        assert item.TestStructure.DateTypeValue.month == value[6]
        assert item.TestStructure.DateTypeValue.day == value[7]
        assert item.TestStructure.DateTypeValue.timezone.hours == value[12]
        assert item.TestStructure.DateTypeValue.timezone.minutes == value[13]
        assert item.TestStructure.TimeTypeValue.hour == value[8]
        assert item.TestStructure.TimeTypeValue.minute == value[9]
        assert item.TestStructure.TimeTypeValue.second == value[10]
        assert item.TestStructure.TimeTypeValue.timezone.hours == value[12]
        assert item.TestStructure.TimeTypeValue.timezone.minutes == value[13]
        assert item.TestStructure.TimestampTypeValue.year == value[5]
        assert item.TestStructure.TimestampTypeValue.month == value[6]
        assert item.TestStructure.TimestampTypeValue.day == value[7]
        assert item.TestStructure.TimestampTypeValue.hour == value[8]
        assert item.TestStructure.TimestampTypeValue.minute == value[9]
        assert item.TestStructure.TimestampTypeValue.second == value[10]
        assert item.TestStructure.TimestampTypeValue.millisecond == value[11]
        assert item.TestStructure.TimestampTypeValue.timezone.hours == value[12]
        assert item.TestStructure.TimestampTypeValue.timezone.minutes == value[13]
        assert (
            item.TestStructure.AnyTypeValue.type
            == "<DataType><Basic>String</Basic></DataType>"
        )

        expected_embedded_message = String(value=value[14]).SerializeToString()
        assert item.TestStructure.AnyTypeValue.payload == (
            b"\x0a"  # type of field 1: message
            + len(expected_embedded_message).to_bytes(1, byteorder="big")
            + expected_embedded_message
        )


def test_read_structure_list(listdatatypetest_stub):
    """
    ListDataTypeTest.EchoStructureList with an empty parameters message should return a message containing
    a list with the following Structure values for the first element:
    string value = 'SiLA2_Test_String_Value_1'
    integer value = 5124
    real value = 3.1415926
    boolean value = true
    binary value (embedded string) = 'Binary_String_Value_1'
    date value = 05.08.2022 respective 08/05/2022
    time value = 12:34:56.789
    time stamp value = 2022-08-05 12:34:56.789
    any type value (string) = 'Any_Type_String_Value_1'

    For the second and third element:
    the last character of the strings changes to '2' respective '3'
    the numeric values are incremented by 1
    the boolean values becomes false for element 2 and true for element 3
    for the date value day, month and year are incremented by 1
    for the time value milliseconds, seconds, minutes and hours are incremented by 1
    for the time stamp value day, month, year, milliseconds, seconds, minutes and hours are incremented by 1.
    """
    response = listdatatypetest_stub.Get_StructureList(Get_StructureList_Parameters())
    assert len(response.StructureList) == 3
    assert (
        response.StructureList[0].TestStructure.StringTypeValue.value
        == "SiLA2_Test_String_Value_1"
    )
    assert response.StructureList[0].TestStructure.IntegerTypeValue.value == 5124
    assert math.isclose(
        response.StructureList[0].TestStructure.RealTypeValue.value, 3.1415926
    )
    assert response.StructureList[0].TestStructure.BooleanTypeValue.value is True
    assert (
        response.StructureList[0].TestStructure.BinaryTypeValue.value
        == b"Binary_String_Value_1"
    )
    assert response.StructureList[0].TestStructure.DateTypeValue.year == 2022
    assert response.StructureList[0].TestStructure.DateTypeValue.month == 8
    assert response.StructureList[0].TestStructure.DateTypeValue.day == 5
    assert response.StructureList[0].TestStructure.DateTypeValue.timezone.hours == 2
    assert response.StructureList[0].TestStructure.DateTypeValue.timezone.minutes == 0
    assert response.StructureList[0].TestStructure.TimeTypeValue.hour == 12
    assert response.StructureList[0].TestStructure.TimeTypeValue.minute == 34
    assert response.StructureList[0].TestStructure.TimeTypeValue.second == 56
    assert response.StructureList[0].TestStructure.TimeTypeValue.timezone.hours == 2
    assert response.StructureList[0].TestStructure.TimeTypeValue.timezone.minutes == 0
    assert response.StructureList[0].TestStructure.TimestampTypeValue.year == 2022
    assert response.StructureList[0].TestStructure.TimestampTypeValue.month == 8
    assert response.StructureList[0].TestStructure.TimestampTypeValue.day == 5
    assert response.StructureList[0].TestStructure.TimestampTypeValue.hour == 12
    assert response.StructureList[0].TestStructure.TimestampTypeValue.minute == 34
    assert response.StructureList[0].TestStructure.TimestampTypeValue.second == 56
    assert (
        response.StructureList[0].TestStructure.TimestampTypeValue.timezone.hours == 2
    )
    assert (
        response.StructureList[0].TestStructure.TimestampTypeValue.timezone.minutes == 0
    )
    assert (
        response.StructureList[0].TestStructure.AnyTypeValue.type
        == "<DataType><Basic>String</Basic></DataType>"
    )

    expected_embedded_message = String(
        value="Any_Type_String_Value_1"
    ).SerializeToString()
    assert response.StructureList[0].TestStructure.AnyTypeValue.payload == (
        b"\x0a"  # type of field 1: message
        + len(expected_embedded_message).to_bytes(1, byteorder="big")
        + expected_embedded_message
    )

    assert (
        response.StructureList[1].TestStructure.StringTypeValue.value
        == "SiLA2_Test_String_Value_2"
    )
    assert response.StructureList[1].TestStructure.IntegerTypeValue.value == 5125
    assert math.isclose(
        response.StructureList[1].TestStructure.RealTypeValue.value, 4.1415926
    )
    assert response.StructureList[1].TestStructure.BooleanTypeValue.value is False
    assert (
        response.StructureList[1].TestStructure.BinaryTypeValue.value
        == b"Binary_String_Value_2"
    )
    assert response.StructureList[1].TestStructure.DateTypeValue.year == 2023
    assert response.StructureList[1].TestStructure.DateTypeValue.month == 9
    assert response.StructureList[1].TestStructure.DateTypeValue.day == 6
    assert response.StructureList[1].TestStructure.DateTypeValue.timezone.hours == 2
    assert response.StructureList[1].TestStructure.DateTypeValue.timezone.minutes == 0
    assert response.StructureList[1].TestStructure.TimeTypeValue.hour == 13
    assert response.StructureList[1].TestStructure.TimeTypeValue.minute == 35
    assert response.StructureList[1].TestStructure.TimeTypeValue.second == 57
    assert response.StructureList[1].TestStructure.TimeTypeValue.timezone.hours == 2
    assert response.StructureList[1].TestStructure.TimeTypeValue.timezone.minutes == 0
    assert response.StructureList[1].TestStructure.TimestampTypeValue.year == 2023
    assert response.StructureList[1].TestStructure.TimestampTypeValue.month == 9
    assert response.StructureList[1].TestStructure.TimestampTypeValue.day == 6
    assert response.StructureList[1].TestStructure.TimestampTypeValue.hour == 13
    assert response.StructureList[1].TestStructure.TimestampTypeValue.minute == 35
    assert response.StructureList[1].TestStructure.TimestampTypeValue.second == 57
    assert (
        response.StructureList[1].TestStructure.TimestampTypeValue.timezone.hours == 2
    )
    assert (
        response.StructureList[1].TestStructure.TimestampTypeValue.timezone.minutes == 0
    )
    assert (
        response.StructureList[1].TestStructure.AnyTypeValue.type
        == "<DataType><Basic>String</Basic></DataType>"
    )

    expected_embedded_message = String(
        value="Any_Type_String_Value_2"
    ).SerializeToString()
    assert response.StructureList[1].TestStructure.AnyTypeValue.payload == (
        b"\x0a"  # type of field 1: message
        + len(expected_embedded_message).to_bytes(1, byteorder="big")
        + expected_embedded_message
    )

    assert (
        response.StructureList[2].TestStructure.StringTypeValue.value
        == "SiLA2_Test_String_Value_3"
    )
    assert response.StructureList[2].TestStructure.IntegerTypeValue.value == 5126
    assert math.isclose(
        response.StructureList[2].TestStructure.RealTypeValue.value, 5.1415926
    )
    assert response.StructureList[2].TestStructure.BooleanTypeValue.value is True
    assert (
        response.StructureList[2].TestStructure.BinaryTypeValue.value
        == b"Binary_String_Value_3"
    )
    assert response.StructureList[2].TestStructure.DateTypeValue.year == 2024
    assert response.StructureList[2].TestStructure.DateTypeValue.month == 10
    assert response.StructureList[2].TestStructure.DateTypeValue.day == 7
    assert response.StructureList[2].TestStructure.DateTypeValue.timezone.hours == 2
    assert response.StructureList[2].TestStructure.DateTypeValue.timezone.minutes == 0
    assert response.StructureList[2].TestStructure.TimeTypeValue.hour == 14
    assert response.StructureList[2].TestStructure.TimeTypeValue.minute == 36
    assert response.StructureList[2].TestStructure.TimeTypeValue.second == 58
    assert response.StructureList[2].TestStructure.TimeTypeValue.timezone.hours == 2
    assert response.StructureList[2].TestStructure.TimeTypeValue.timezone.minutes == 0
    assert response.StructureList[2].TestStructure.TimestampTypeValue.year == 2024
    assert response.StructureList[2].TestStructure.TimestampTypeValue.month == 10
    assert response.StructureList[2].TestStructure.TimestampTypeValue.day == 7
    assert response.StructureList[2].TestStructure.TimestampTypeValue.hour == 14
    assert response.StructureList[2].TestStructure.TimestampTypeValue.minute == 36
    assert response.StructureList[2].TestStructure.TimestampTypeValue.second == 58
    assert (
        response.StructureList[2].TestStructure.TimestampTypeValue.timezone.hours == 2
    )
    assert (
        response.StructureList[2].TestStructure.TimestampTypeValue.timezone.minutes == 0
    )
    assert (
        response.StructureList[2].TestStructure.AnyTypeValue.type
        == "<DataType><Basic>String</Basic></DataType>"
    )

    expected_embedded_message = String(
        value="Any_Type_String_Value_3"
    ).SerializeToString()
    assert response.StructureList[2].TestStructure.AnyTypeValue.payload == (
        b"\x0a"  # type of field 1: message
        + len(expected_embedded_message).to_bytes(1, byteorder="big")
        + expected_embedded_message
    )
