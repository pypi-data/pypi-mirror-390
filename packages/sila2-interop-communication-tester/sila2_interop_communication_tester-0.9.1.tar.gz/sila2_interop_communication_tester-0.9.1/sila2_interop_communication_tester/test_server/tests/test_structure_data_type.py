import math

from sila2_interop_communication_tester.grpc_stubs import SiLAFramework_pb2


def test_echo_structure_value_called_with_defaults(server_calls):
    calls = server_calls["StructureDataTypeTest.EchoStructureValue"]
    expected_string_message = SiLAFramework_pb2.String(value="SiLA2_Any_Type_String_Value")
    assert any(
        call.request.StructureValue.TestStructure.StringTypeValue.value == "SiLA2_Test_String_Value"
        and call.request.StructureValue.TestStructure.IntegerTypeValue.value == 5124
        and math.isclose(call.request.StructureValue.TestStructure.RealTypeValue.value, 3.1415926)
        and call.request.StructureValue.TestStructure.BooleanTypeValue.value is True
        and call.request.StructureValue.TestStructure.BinaryTypeValue.value == b"SiLA2_Binary_String_Value"
        and call.request.StructureValue.TestStructure.DateTypeValue.year == 2022
        and call.request.StructureValue.TestStructure.DateTypeValue.month == 8
        and call.request.StructureValue.TestStructure.DateTypeValue.day == 5
        and call.request.StructureValue.TestStructure.DateTypeValue.timezone.hours == 2
        and call.request.StructureValue.TestStructure.DateTypeValue.timezone.minutes == 0
        and call.request.StructureValue.TestStructure.TimeTypeValue.hour == 12
        and call.request.StructureValue.TestStructure.TimeTypeValue.minute == 34
        and call.request.StructureValue.TestStructure.TimeTypeValue.second == 56
        and call.request.StructureValue.TestStructure.TimeTypeValue.timezone.hours == 2
        and call.request.StructureValue.TestStructure.TimeTypeValue.timezone.minutes == 0
        and call.request.StructureValue.TestStructure.TimestampTypeValue.year == 2022
        and call.request.StructureValue.TestStructure.TimestampTypeValue.month == 8
        and call.request.StructureValue.TestStructure.TimestampTypeValue.day == 5
        and call.request.StructureValue.TestStructure.TimestampTypeValue.hour == 12
        and call.request.StructureValue.TestStructure.TimestampTypeValue.minute == 34
        and call.request.StructureValue.TestStructure.TimestampTypeValue.second == 56
        and call.request.StructureValue.TestStructure.TimestampTypeValue.timezone.hours == 2
        and call.request.StructureValue.TestStructure.TimestampTypeValue.timezone.minutes == 0
        and call.request.StructureValue.TestStructure.AnyTypeValue.type == "<DataType><Basic>String</Basic></DataType>"
        and call.request.StructureValue.TestStructure.AnyTypeValue.payload == (
            b"\x0a"  # type of field 1: message
            + len(expected_string_message.SerializeToString()).to_bytes(1, byteorder="big")
            + expected_string_message.SerializeToString()
        )
        for call in calls
    )


def test_echo_deep_structure_value_called_with_defaults(server_calls):
    calls = server_calls["StructureDataTypeTest.EchoDeepStructureValue"]
    assert any(
        call.request.DeepStructureValue.DeepStructure.OuterStringTypeValue.value == "Outer_Test_String"
        and call.request.DeepStructureValue.DeepStructure.OuterIntegerTypeValue.value == 1111
        and call.request.DeepStructureValue.DeepStructure.MiddleStructure.MiddleStringTypeValue.value
        == "Middle_Test_String"
        and call.request.DeepStructureValue.DeepStructure.MiddleStructure.MiddleIntegerTypeValue.value == 2222
        and call.request.DeepStructureValue.DeepStructure.MiddleStructure.InnerStructure.InnerStringTypeValue.value
        == "Inner_Test_String"
        and call.request.DeepStructureValue.DeepStructure.MiddleStructure.InnerStructure.InnerIntegerTypeValue.value == 3333
        for call in calls
    )


def test_structure_value_requested(server_calls):
    calls = server_calls["StructureDataTypeTest.Get_StructureValue"]
    assert any(call.successful for call in calls)


def test_deep_structure_value_requested(server_calls):
    calls = server_calls["StructureDataTypeTest.Get_DeepStructureValue"]
    assert any(call.successful for call in calls)
