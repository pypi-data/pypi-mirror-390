import math

from sila2_interop_communication_tester.grpc_stubs import SiLAFramework_pb2


def test_echo_string_list_called_with_sila_2_is_great(server_calls):
    calls = server_calls["ListDataTypeTest.EchoStringList"]
    assert any(
        call.request.StringList
        == [
            SiLAFramework_pb2.String(value="SiLA 2"),
            SiLAFramework_pb2.String(value="is"),
            SiLAFramework_pb2.String(value="great"),
        ]
        for call in calls
    )


def test_echo_integer_list_called_with_1_2_3(server_calls):
    calls = server_calls["ListDataTypeTest.EchoIntegerList"]
    assert any(
        call.request.IntegerList
        == [
            SiLAFramework_pb2.Integer(value=1),
            SiLAFramework_pb2.Integer(value=2),
            SiLAFramework_pb2.Integer(value=3),
        ]
        for call in calls
    )


def test_echo_structure_list_called_with_defaults(server_calls):
    calls = server_calls["ListDataTypeTest.EchoStructureList"]
    assert any(
        len(call.request.StructureList) == 3
        and call.request.StructureList[0].TestStructure.StringTypeValue.value
        == "SiLA2_Test_String_Value_1"
        and call.request.StructureList[0].TestStructure.IntegerTypeValue.value == 5124
        and math.isclose(
            call.request.StructureList[0].TestStructure.RealTypeValue.value, 3.1415926
        )
        and call.request.StructureList[0].TestStructure.BooleanTypeValue.value is True
        and call.request.StructureList[0].TestStructure.BinaryTypeValue.value
        == b"Binary_String_Value_1"
        and call.request.StructureList[0].TestStructure.DateTypeValue.year == 2022
        and call.request.StructureList[0].TestStructure.DateTypeValue.month == 8
        and call.request.StructureList[0].TestStructure.DateTypeValue.day == 5
        and call.request.StructureList[0].TestStructure.DateTypeValue.timezone.hours
        == 2
        and call.request.StructureList[0].TestStructure.DateTypeValue.timezone.minutes
        == 0
        and call.request.StructureList[0].TestStructure.TimeTypeValue.hour == 12
        and call.request.StructureList[0].TestStructure.TimeTypeValue.minute == 34
        and call.request.StructureList[0].TestStructure.TimeTypeValue.second == 56
        and call.request.StructureList[0].TestStructure.TimeTypeValue.timezone.hours
        == 2
        and call.request.StructureList[0].TestStructure.TimeTypeValue.timezone.minutes
        == 0
        and call.request.StructureList[0].TestStructure.TimestampTypeValue.year == 2022
        and call.request.StructureList[0].TestStructure.TimestampTypeValue.month == 8
        and call.request.StructureList[0].TestStructure.TimestampTypeValue.day == 5
        and call.request.StructureList[0].TestStructure.TimestampTypeValue.hour == 12
        and call.request.StructureList[0].TestStructure.TimestampTypeValue.minute == 34
        and call.request.StructureList[0].TestStructure.TimestampTypeValue.second == 56
        and call.request.StructureList[
            0
        ].TestStructure.TimestampTypeValue.timezone.hours
        == 2
        and call.request.StructureList[
            0
        ].TestStructure.TimestampTypeValue.timezone.minutes
        == 0
        and call.request.StructureList[0].TestStructure.AnyTypeValue.type
        == "<DataType><Basic>String</Basic></DataType>"
        and call.request.StructureList[0].TestStructure.AnyTypeValue.payload
        == b"\x0a\x19\x0a\x17Any_Type_String_Value_1"  # field 1: String with 0x19 bytes
        and call.request.StructureList[1].TestStructure.StringTypeValue.value
        == "SiLA2_Test_String_Value_2"
        and call.request.StructureList[1].TestStructure.IntegerTypeValue.value == 5125
        and math.isclose(
            call.request.StructureList[1].TestStructure.RealTypeValue.value, 4.1415926
        )
        and call.request.StructureList[1].TestStructure.BooleanTypeValue.value is False
        and call.request.StructureList[1].TestStructure.BinaryTypeValue.value
        == b"Binary_String_Value_2"
        and call.request.StructureList[1].TestStructure.DateTypeValue.year == 2023
        and call.request.StructureList[1].TestStructure.DateTypeValue.month == 9
        and call.request.StructureList[1].TestStructure.DateTypeValue.day == 6
        and call.request.StructureList[1].TestStructure.DateTypeValue.timezone.hours
        == 2
        and call.request.StructureList[1].TestStructure.DateTypeValue.timezone.minutes
        == 0
        and call.request.StructureList[1].TestStructure.TimeTypeValue.hour == 13
        and call.request.StructureList[1].TestStructure.TimeTypeValue.minute == 35
        and call.request.StructureList[1].TestStructure.TimeTypeValue.second == 57
        and call.request.StructureList[1].TestStructure.TimeTypeValue.timezone.hours
        == 2
        and call.request.StructureList[1].TestStructure.TimeTypeValue.timezone.minutes
        == 0
        and call.request.StructureList[1].TestStructure.TimestampTypeValue.year == 2023
        and call.request.StructureList[1].TestStructure.TimestampTypeValue.month == 9
        and call.request.StructureList[1].TestStructure.TimestampTypeValue.day == 6
        and call.request.StructureList[1].TestStructure.TimestampTypeValue.hour == 13
        and call.request.StructureList[1].TestStructure.TimestampTypeValue.minute == 35
        and call.request.StructureList[1].TestStructure.TimestampTypeValue.second == 57
        and call.request.StructureList[
            1
        ].TestStructure.TimestampTypeValue.timezone.hours
        == 2
        and call.request.StructureList[
            1
        ].TestStructure.TimestampTypeValue.timezone.minutes
        == 0
        and call.request.StructureList[1].TestStructure.AnyTypeValue.type
        == "<DataType><Basic>String</Basic></DataType>"
        and call.request.StructureList[1].TestStructure.AnyTypeValue.payload
        == b"\x0a\x19\x0a\x17Any_Type_String_Value_2"  # field 1: String with 0x19 bytes
        and call.request.StructureList[2].TestStructure.StringTypeValue.value
        == "SiLA2_Test_String_Value_3"
        and call.request.StructureList[2].TestStructure.IntegerTypeValue.value == 5126
        and math.isclose(
            call.request.StructureList[2].TestStructure.RealTypeValue.value, 5.1415926
        )
        and call.request.StructureList[2].TestStructure.BooleanTypeValue.value is True
        and call.request.StructureList[2].TestStructure.BinaryTypeValue.value
        == b"Binary_String_Value_3"
        and call.request.StructureList[2].TestStructure.DateTypeValue.year == 2024
        and call.request.StructureList[2].TestStructure.DateTypeValue.month == 10
        and call.request.StructureList[2].TestStructure.DateTypeValue.day == 7
        and call.request.StructureList[2].TestStructure.DateTypeValue.timezone.hours
        == 2
        and call.request.StructureList[2].TestStructure.DateTypeValue.timezone.minutes
        == 0
        and call.request.StructureList[2].TestStructure.TimeTypeValue.hour == 14
        and call.request.StructureList[2].TestStructure.TimeTypeValue.minute == 36
        and call.request.StructureList[2].TestStructure.TimeTypeValue.second == 58
        and call.request.StructureList[2].TestStructure.TimeTypeValue.timezone.hours
        == 2
        and call.request.StructureList[2].TestStructure.TimeTypeValue.timezone.minutes
        == 0
        and call.request.StructureList[2].TestStructure.TimestampTypeValue.year == 2024
        and call.request.StructureList[2].TestStructure.TimestampTypeValue.month == 10
        and call.request.StructureList[2].TestStructure.TimestampTypeValue.day == 7
        and call.request.StructureList[2].TestStructure.TimestampTypeValue.hour == 14
        and call.request.StructureList[2].TestStructure.TimestampTypeValue.minute == 36
        and call.request.StructureList[2].TestStructure.TimestampTypeValue.second == 58
        and call.request.StructureList[
            2
        ].TestStructure.TimestampTypeValue.timezone.hours
        == 2
        and call.request.StructureList[
            2
        ].TestStructure.TimestampTypeValue.timezone.minutes
        == 0
        and call.request.StructureList[2].TestStructure.AnyTypeValue.type
        == "<DataType><Basic>String</Basic></DataType>"
        and call.request.StructureList[2].TestStructure.AnyTypeValue.payload
        == b"\x0a\x19\x0a\x17Any_Type_String_Value_3"  # field 1: String with 0x19 bytes
        for call in calls
    )


def test_empty_string_list_requested(server_calls):
    calls = server_calls["ListDataTypeTest.Get_EmptyStringList"]
    assert any(call.successful for call in calls)


def test_string_list_requested(server_calls):
    calls = server_calls["ListDataTypeTest.Get_StringList"]
    assert any(call.successful for call in calls)


def test_integer_list_requested(server_calls):
    calls = server_calls["ListDataTypeTest.Get_IntegerList"]
    assert any(call.successful for call in calls)


def test_structure_list_requested(server_calls):
    calls = server_calls["ListDataTypeTest.Get_StructureList"]
    assert any(call.successful for call in calls)
