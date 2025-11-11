import math

import pytest

from sila2_interop_communication_tester.grpc_stubs.BasicDataTypesTest_pb2 import (
    EchoRealValue_Parameters,
    Get_RealValue_Parameters,
)
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import Real
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_validation_error,
)


def test_echo_real_value_rejects_empty_parameter_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoRealValue should fail with a Validation Error if the parameter message was empty."""
    with raises_validation_error(
        "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoRealValue/Parameter/RealValue"
    ):
        basicdatatypestest_stub.EchoRealValue(EchoRealValue_Parameters())


def test_echo_real_value_with_empty_real_message(basicdatatypestest_stub):
    """BasicDataTypesTest.EchoRealValue should work when provided with an empty Real message."""
    response = basicdatatypestest_stub.EchoRealValue(
        EchoRealValue_Parameters(RealValue=Real())
    )

    assert response.HasField("ReceivedValue")
    assert math.isclose(response.ReceivedValue.value, 0.0)


@pytest.mark.parametrize(
    "value",
    [
        0.0,
        3.1415926,
        -3.1415926,
        pytest.param(2.2250738585072014e-308, id="min"),
        pytest.param(1.7976931348623157e308, id="max"),
    ],
)
def test_echo_real_value(basicdatatypestest_stub, value):
    """BasicDataTypesTest.EchoRealValue should work when provided with a Real message."""
    response = basicdatatypestest_stub.EchoRealValue(
        EchoRealValue_Parameters(RealValue=Real(value=value))
    )

    assert response.HasField("ReceivedValue")
    assert math.isclose(response.ReceivedValue.value, value)


def test_read_real_value(basicdatatypestest_stub):
    """
    BasicDataTypesTest.Get_RealValue with an empty parameters message should return a message containing
    the real `value` 3.1415926.
    """
    response = basicdatatypestest_stub.Get_RealValue(Get_RealValue_Parameters())
    assert response.HasField("RealValue")
    assert math.isclose(response.RealValue.value, 3.1415926)
