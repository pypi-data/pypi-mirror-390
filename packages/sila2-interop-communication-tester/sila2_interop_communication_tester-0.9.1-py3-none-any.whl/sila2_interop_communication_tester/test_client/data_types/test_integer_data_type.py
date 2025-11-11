import pytest

from sila2_interop_communication_tester.grpc_stubs.BasicDataTypesTest_pb2 import (
    EchoIntegerValue_Parameters,
    Get_IntegerValue_Parameters,
)
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import Integer
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_validation_error,
)


def test_echo_integer_value_rejects_empty_parameter_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoIntegerValue should fail with a Validation Error if the parameter message was empty."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoIntegerValue/Parameter/IntegerValue"
    ):
        basicdatatypestest_stub.EchoIntegerValue(EchoIntegerValue_Parameters())


def test_echo_integer_value_with_empty_integer_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoIntegerValue should work when provided with an empty Integer message."""
    response = basicdatatypestest_stub.EchoIntegerValue(
        EchoIntegerValue_Parameters(IntegerValue=Integer())
    )

    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue.value == 0


@pytest.mark.parametrize(
    "value",
    [
        0,
        5124,
        -5124,
        pytest.param(-(2**63), id="min: -(2**63)"),
        pytest.param(2**63 - 1, id="max: 2**63-1"),
    ],
)
def test_echo_integer_value(basicdatatypestest_stub, value):
    """BasicDataTypesTest.EchoIntegerValue should work when provided with a Integer message."""
    response = basicdatatypestest_stub.EchoIntegerValue(
        EchoIntegerValue_Parameters(IntegerValue=Integer(value=value))
    )

    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue.value == value


def test_read_integer_value(basicdatatypestest_stub):
    """
    BasicDataTypesTest.Get_IntegerValue with an empty parameters message should return a message containing
    the integer `value` 5124.
    """
    response = basicdatatypestest_stub.Get_IntegerValue(Get_IntegerValue_Parameters())
    assert response.HasField("IntegerValue")
    assert response.IntegerValue.value == 5124
