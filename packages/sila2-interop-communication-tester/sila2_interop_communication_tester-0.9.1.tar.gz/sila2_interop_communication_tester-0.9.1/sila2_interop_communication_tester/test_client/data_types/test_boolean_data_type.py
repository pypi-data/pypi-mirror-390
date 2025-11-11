import pytest

from sila2_interop_communication_tester.grpc_stubs.BasicDataTypesTest_pb2 import (
    EchoBooleanValue_Parameters,
    Get_BooleanValue_Parameters,
)
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import Boolean
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_validation_error,
)


def test_echo_boolean_value_rejects_empty_parameter_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoBooleanValue should fail with a Validation Error if the parameter message was empty."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoBooleanValue/Parameter/BooleanValue"
    ):
        basicdatatypestest_stub.EchoBooleanValue(EchoBooleanValue_Parameters())


def test_echo_boolean_value_with_empty_boolean_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoBooleanValue should work when provided with an empty Boolean message."""
    response = basicdatatypestest_stub.EchoBooleanValue(
        EchoBooleanValue_Parameters(BooleanValue=Boolean())
    )

    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue.value is False


@pytest.mark.parametrize("value", [False, True])
def test_echo_boolean_value(basicdatatypestest_stub, value):
    """BasicDataTypesTest.EchoBooleanValue should work when provided with a Boolean message."""
    response = basicdatatypestest_stub.EchoBooleanValue(
        EchoBooleanValue_Parameters(BooleanValue=Boolean(value=value))
    )

    assert response.HasField("ReceivedValue")
    assert response.ReceivedValue.value is value


def test_read_boolean_value(basicdatatypestest_stub):
    """
    BasicDataTypesTest.Get_BooleanValue with an empty parameters message should return a message containing
    the boolean `value` true.
    """
    response = basicdatatypestest_stub.Get_BooleanValue(Get_BooleanValue_Parameters())
    assert response.HasField("BooleanValue")
    assert response.BooleanValue.value is True
