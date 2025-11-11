import pytest
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
from sila2_interop_communication_tester.grpc_stubs.StructureDataTypeTest_pb2 import (
    DataType_DeepStructure,
    DataType_TestStructure,
    EchoDeepStructureValue_Parameters,
    EchoStructureValue_Parameters,
    Get_DeepStructureValue_Parameters,
    Get_StructureValue_Parameters,
)
from sila2_interop_communication_tester.helpers.protobuf_helpers import (
    create_any_message,
)
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_validation_error,
)


def test_echo_structure_value_rejects_empty_parameter_message(
    structuredatatypetest_stub,
):
    """
    StructureDataTypeTest.EchoStructureValue should fail with a Validation Error if the parameter message was empty.
    """
    with raises_validation_error(
        "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue"
    ):
        structuredatatypetest_stub.EchoStructureValue(EchoStructureValue_Parameters())


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(
            ("", 0, 0.0, False, b"", 1, 1, 1, 0, 0, 0, 0, 0, 0, b""),
            id="default-values",
        ),
        pytest.param(
            (
                "SiLA2_Test_String_Value",
                5124,
                3.1415926,
                True,
                b"SiLA2_Binary_String_Value",
                2022,
                8,
                5,
                12,
                34,
                56,
                789,
                2,
                0,
                "SiLA2_Any_Type_String_Value",
            ),
            id="custom-values",
        ),
    ],
)
def test_echo_structure_value(structuredatatypetest_stub, value):
    """StructureDataTypeTest.EchoStructureValue should work when provided with a Structure message."""
    response = structuredatatypetest_stub.EchoStructureValue(
        EchoStructureValue_Parameters(
            StructureValue=DataType_TestStructure(
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
        )
    )

    assert response.ReceivedValues.TestStructure.StringTypeValue.value == value[0]
    assert response.ReceivedValues.TestStructure.IntegerTypeValue.value == value[1]
    assert math.isclose(response.ReceivedValues.TestStructure.RealTypeValue.value, value[2])
    assert response.ReceivedValues.TestStructure.BooleanTypeValue.value == value[3]
    assert response.ReceivedValues.TestStructure.BinaryTypeValue.value == value[4]
    assert response.ReceivedValues.TestStructure.DateTypeValue.year == value[5]
    assert response.ReceivedValues.TestStructure.DateTypeValue.month == value[6]
    assert response.ReceivedValues.TestStructure.DateTypeValue.day == value[7]
    assert (
        response.ReceivedValues.TestStructure.DateTypeValue.timezone.hours == value[12]
    )
    assert (
        response.ReceivedValues.TestStructure.DateTypeValue.timezone.minutes
        == value[13]
    )
    assert response.ReceivedValues.TestStructure.TimeTypeValue.hour == value[8]
    assert response.ReceivedValues.TestStructure.TimeTypeValue.minute == value[9]
    assert response.ReceivedValues.TestStructure.TimeTypeValue.second == value[10]
    assert (
        response.ReceivedValues.TestStructure.TimeTypeValue.timezone.hours == value[12]
    )
    assert (
        response.ReceivedValues.TestStructure.TimeTypeValue.timezone.minutes
        == value[13]
    )
    assert response.ReceivedValues.TestStructure.TimestampTypeValue.year == value[5]
    assert response.ReceivedValues.TestStructure.TimestampTypeValue.month == value[6]
    assert response.ReceivedValues.TestStructure.TimestampTypeValue.day == value[7]
    assert response.ReceivedValues.TestStructure.TimestampTypeValue.hour == value[8]
    assert response.ReceivedValues.TestStructure.TimestampTypeValue.minute == value[9]
    assert response.ReceivedValues.TestStructure.TimestampTypeValue.second == value[10]
    assert (
        response.ReceivedValues.TestStructure.TimestampTypeValue.timezone.hours
        == value[12]
    )
    assert (
        response.ReceivedValues.TestStructure.TimestampTypeValue.timezone.minutes
        == value[13]
    )
    assert (
        response.ReceivedValues.TestStructure.AnyTypeValue.type
        == "<DataType><Basic>String</Basic></DataType>"
    )

    expected_embedded_message = String(value=value[14]).SerializeToString()
    assert response.ReceivedValues.TestStructure.AnyTypeValue.payload == (
        b"\x0a"  # type of field 1: message
        + len(expected_embedded_message).to_bytes(1, byteorder="big")
        + expected_embedded_message
    )


def test_read_structure_value(structuredatatypetest_stub):
    """
    StructureDataTypeTest.Get_StructureValue with an empty parameters message should return a message containing
    a structure with the following elements values:
    - String value = 'SiLA2_Test_String_Value'
    - Integer value = 5124
    - Real value = 3.1415926
    - Boolean value = true
    - Binary value = embedded string 'SiLA2_Binary_String_Value'
    - Date value = 05.08.2022 respective 08/05/2022
    - Time value = 12:34:56.789
    - Timestamp value = 2022-08-05 12:34:56.789
    - Any type value = string 'SiLA2_Any_Type_String_Value'.
    """
    response = structuredatatypetest_stub.Get_StructureValue(
        Get_StructureValue_Parameters()
    )

    assert (
        response.StructureValue.TestStructure.StringTypeValue.value
        == "SiLA2_Test_String_Value"
    )
    assert response.StructureValue.TestStructure.IntegerTypeValue.value == 5124
    assert math.isclose(response.StructureValue.TestStructure.RealTypeValue.value, 3.1415926)
    assert response.StructureValue.TestStructure.BooleanTypeValue.value is True
    assert (
        response.StructureValue.TestStructure.BinaryTypeValue.value
        == b"SiLA2_Binary_String_Value"
    )
    assert response.StructureValue.TestStructure.DateTypeValue.year == 2022
    assert response.StructureValue.TestStructure.DateTypeValue.month == 8
    assert response.StructureValue.TestStructure.DateTypeValue.day == 5
    assert response.StructureValue.TestStructure.DateTypeValue.timezone.hours == 2
    assert response.StructureValue.TestStructure.DateTypeValue.timezone.minutes == 0
    assert response.StructureValue.TestStructure.TimeTypeValue.hour == 12
    assert response.StructureValue.TestStructure.TimeTypeValue.minute == 34
    assert response.StructureValue.TestStructure.TimeTypeValue.second == 56
    assert response.StructureValue.TestStructure.TimeTypeValue.timezone.hours == 2
    assert response.StructureValue.TestStructure.TimeTypeValue.timezone.minutes == 0
    assert response.StructureValue.TestStructure.TimestampTypeValue.year == 2022
    assert response.StructureValue.TestStructure.TimestampTypeValue.month == 8
    assert response.StructureValue.TestStructure.TimestampTypeValue.day == 5
    assert response.StructureValue.TestStructure.TimestampTypeValue.hour == 12
    assert response.StructureValue.TestStructure.TimestampTypeValue.minute == 34
    assert response.StructureValue.TestStructure.TimestampTypeValue.second == 56
    assert response.StructureValue.TestStructure.TimestampTypeValue.timezone.hours == 2
    assert (
        response.StructureValue.TestStructure.TimestampTypeValue.timezone.minutes == 0
    )
    assert (
        response.StructureValue.TestStructure.AnyTypeValue.type
        == "<DataType><Basic>String</Basic></DataType>"
    )

    expected_embedded_message = String(
        value="SiLA2_Any_Type_String_Value"
    ).SerializeToString()
    assert response.StructureValue.TestStructure.AnyTypeValue.payload == (
        b"\x0a"  # type of field 1: message
        + len(expected_embedded_message).to_bytes(1, byteorder="big")
        + expected_embedded_message
    )


def test_echo_deep_structure_value_rejects_empty_parameter_message(
    structuredatatypetest_stub,
):
    """
    StructureDataTypeTest.EchoDeepStructureValue should fail with a Validation Error if the parameter message was empty.
    """
    with raises_validation_error(
        "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoDeepStructureValue/Parameter/DeepStructureValue"
    ):
        structuredatatypetest_stub.EchoDeepStructureValue(
            EchoDeepStructureValue_Parameters()
        )


def test_echo_deep_structure_value_rejects_large_string(structuredatatypetest_stub):
    """
    StructureDataTypeTest.EchoDeepStructureValue should fail with a Validation Error when provided with a string larger
    than 2**21 characters.
    """
    with raises_validation_error(
        "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoDeepStructureValue/Parameter/DeepStructureValue"
    ):
        structuredatatypetest_stub.EchoDeepStructureValue(
            EchoDeepStructureValue_Parameters(
                DeepStructureValue=DataType_DeepStructure(
                    DeepStructure=DataType_DeepStructure.DeepStructure_Struct(
                        OuterStringTypeValue=String(value="Outer_Test_String"),
                        OuterIntegerTypeValue=Integer(value=1111),
                        MiddleStructure=DataType_DeepStructure.DeepStructure_Struct.MiddleStructure_Struct(
                            MiddleStringTypeValue=String(value="Middle_Test_String"),
                            MiddleIntegerTypeValue=Integer(value=22222),
                            InnerStructure=DataType_DeepStructure.DeepStructure_Struct.MiddleStructure_Struct.InnerStructure_Struct(
                                InnerStringTypeValue=String(value=" " * (2**21 + 1)),
                                InnerIntegerTypeValue=Integer(value=3333),
                            ),
                        ),
                    )
                ),
            )
        )


def test_echo_deep_structure_value_with_empty_deep_structure_message(structuredatatypetest_stub):
    """StructureDataTypeTest.EchoDeepStructureValue should reject missing element values."""
    with raises_validation_error("org.silastandard/test/StructureDataTypeTest/v1/Command/EchoDeepStructureValue/Parameter/DeepStructureValue") as err:
        structuredatatypetest_stub.EchoDeepStructureValue(
            EchoDeepStructureValue_Parameters(
                DeepStructureValue=DataType_DeepStructure(
                    DeepStructure=DataType_DeepStructure.DeepStructure_Struct(
                        OuterStringTypeValue=String(value="Outer_Test_String"),
                        OuterIntegerTypeValue=Integer(value=1),
                        MiddleStructure=DataType_DeepStructure.DeepStructure_Struct.MiddleStructure_Struct(
                            MiddleStringTypeValue=String(value="Middle_Test_String"),
                            MiddleIntegerTypeValue=Integer(value=2),
                            InnerStructure=DataType_DeepStructure.DeepStructure_Struct.MiddleStructure_Struct.InnerStructure_Struct(
                                InnerStringTypeValue=String(value="Inner Test String"),
                                InnerIntegerTypeValue=None,  # <- missing value
                            ),
                        ),
                    )
                ),
            )
        )

    assert "InnerIntegerTypeValue" in err.error.message or "Inner Integer Type Value" in err.error.message


@pytest.mark.parametrize(
    "value",
    [
        ("", 0, "", 0, "", 0),
        (
            "Outer_Test_String",
            1111,
            "Middle_Test_String",
            2222,
            "Inner_Test_String",
            3333,
        ),
    ],
    ids=repr,
)
def test_echo_deep_structure_value(structuredatatypetest_stub, value):
    """StructureDataTypeTest.EchoDeepStructureValue should work when provided with a Structure message."""
    response = structuredatatypetest_stub.EchoDeepStructureValue(
        EchoDeepStructureValue_Parameters(
            DeepStructureValue=DataType_DeepStructure(
                DeepStructure=DataType_DeepStructure.DeepStructure_Struct(
                    OuterStringTypeValue=String(value=value[0]),
                    OuterIntegerTypeValue=Integer(value=value[1]),
                    MiddleStructure=DataType_DeepStructure.DeepStructure_Struct.MiddleStructure_Struct(
                        MiddleStringTypeValue=String(value=value[2]),
                        MiddleIntegerTypeValue=Integer(value=value[3]),
                        InnerStructure=DataType_DeepStructure.DeepStructure_Struct.MiddleStructure_Struct.InnerStructure_Struct(
                            InnerStringTypeValue=String(value=value[4]),
                            InnerIntegerTypeValue=Integer(value=value[5]),
                        ),
                    ),
                )
            ),
        )
    )

    assert response.ReceivedValues.DeepStructure.OuterStringTypeValue.value == value[0]
    assert response.ReceivedValues.DeepStructure.OuterIntegerTypeValue.value == value[1]
    assert (
        response.ReceivedValues.DeepStructure.MiddleStructure.MiddleStringTypeValue.value
        == value[2]
    )
    assert (
        response.ReceivedValues.DeepStructure.MiddleStructure.MiddleIntegerTypeValue.value
        == value[3]
    )
    assert (
        response.ReceivedValues.DeepStructure.MiddleStructure.InnerStructure.InnerStringTypeValue.value
        == value[4]
    )
    assert (
        response.ReceivedValues.DeepStructure.MiddleStructure.InnerStructure.InnerIntegerTypeValue.value
        == value[5]
    )


def test_read_deep_structure_value(structuredatatypetest_stub):
    """
    StructureDataTypeTest.Get_DeepStructureValue with an empty parameters message should return a message containing
    a multilevel structure with the following values:
    - string value = 'Outer_Test_String'
    - integer value = 1111
    - middle structure value =
      - string value = 'Middle_Test_String'
      - integer value = 2222
      - inner structure value =
        - string value = 'Inner_Test_String'
        - integer value = 3333.
    """
    response = structuredatatypetest_stub.Get_DeepStructureValue(
        Get_DeepStructureValue_Parameters()
    )

    assert (
        response.DeepStructureValue.DeepStructure.OuterStringTypeValue.value
        == "Outer_Test_String"
    )
    assert response.DeepStructureValue.DeepStructure.OuterIntegerTypeValue.value == 1111
    assert (
        response.DeepStructureValue.DeepStructure.MiddleStructure.MiddleStringTypeValue.value
        == "Middle_Test_String"
    )
    assert (
        response.DeepStructureValue.DeepStructure.MiddleStructure.MiddleIntegerTypeValue.value
        == 2222
    )
    assert (
        response.DeepStructureValue.DeepStructure.MiddleStructure.InnerStructure.InnerStringTypeValue.value
        == "Inner_Test_String"
    )
    assert (
        response.DeepStructureValue.DeepStructure.MiddleStructure.InnerStructure.InnerIntegerTypeValue.value
        == 3333
    )
