import pytest

from sila2_interop_communication_tester.grpc_stubs.BasicDataTypesTest_pb2 import (
    EchoStringValue_Parameters,
    Get_StringValue_Parameters,
)
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import String
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_validation_error,
)


def test_echo_string_value_rejects_empty_parameter_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoStringValue should fail with a Validation Error if the parameter message was empty."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoStringValue/Parameter/StringValue"
    ):
        basicdatatypestest_stub.EchoStringValue(EchoStringValue_Parameters())


def test_echo_string_value_rejects_large_string(basicdatatypestest_stub):
    """
    BasicDataTypesTest.EchoStringValue should fail with a Validation Error when provided with a string larger than 2**21
    characters.
    """
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoStringValue/Parameter/StringValue"
    ):
        basicdatatypestest_stub.EchoStringValue(
            EchoStringValue_Parameters(StringValue=String(value=" " * (2**21 + 1)))
        )


def test_echo_string_value_with_empty_string_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoStringValue should work when provided with an empty String message."""
    response = basicdatatypestest_stub.EchoStringValue(
        EchoStringValue_Parameters(StringValue=String())
    )

    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue.value == ""


@pytest.mark.parametrize(
    "value",
    [
        "",
        "SiLA2_Test_String_Value",
        pytest.param(" " * 2**21, id="max: ' ' * 2^21"),
    ],
    ids=repr,
)
def test_echo_string_value(basicdatatypestest_stub, value):
    """BasicDataTypesTest.EchoStringValue should work when provided with a String message."""
    response = basicdatatypestest_stub.EchoStringValue(
        EchoStringValue_Parameters(StringValue=String(value=value))
    )

    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue.value == value


def test_read_string_value(basicdatatypestest_stub):
    """
    BasicDataTypesTest.Get_StringValue with an empty parameters message should return a message containing
    the string `value` "SiLA2_Test_String_Value".
    """
    response = basicdatatypestest_stub.Get_StringValue(Get_StringValue_Parameters())
    assert response.HasField("StringValue")
    assert response.StringValue.value == "SiLA2_Test_String_Value"
