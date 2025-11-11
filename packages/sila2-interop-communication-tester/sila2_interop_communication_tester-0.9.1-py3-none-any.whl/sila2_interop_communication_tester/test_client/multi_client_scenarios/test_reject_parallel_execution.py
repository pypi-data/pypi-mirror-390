import time
import uuid

from sila2_interop_communication_tester.grpc_stubs.MultiClientTest_pb2 import RejectParallelExecution_Parameters
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import CommandExecutionUUID, Real
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_command_execution_not_accepted_error,
    raises_invalid_command_execution_uuid_error,
    raises_validation_error,
)


def test_rejects_missing_parameter(multiclienttest_stub):
    with raises_validation_error(
        "org.silastandard/test/MultiClientTest/v1/Command/RejectParallelExecution/Parameter/Duration"
    ):
        multiclienttest_stub.RejectParallelExecution(RejectParallelExecution_Parameters())


def test_info_rejects_non_uuid_strings(multiclienttest_stub):
    stream = multiclienttest_stub.RejectParallelExecution_Info(CommandExecutionUUID(value="abcde"))
    with raises_invalid_command_execution_uuid_error():
        next(stream)


def test_info_rejects_unknown_uuids(multiclienttest_stub):
    stream = multiclienttest_stub.RejectParallelExecution_Info(CommandExecutionUUID(value=str(uuid.uuid4())))
    with raises_invalid_command_execution_uuid_error():
        next(stream)


def test_result_rejects_non_uuid_strings(multiclienttest_stub):
    with raises_invalid_command_execution_uuid_error():
        multiclienttest_stub.RejectParallelExecution_Result(CommandExecutionUUID(value="abcde"))


def test_result_rejects_unknown_uuids(multiclienttest_stub):
    with raises_invalid_command_execution_uuid_error():
        multiclienttest_stub.RejectParallelExecution_Result(CommandExecutionUUID(value=str(uuid.uuid4())))


def test_parallel_execution_is_rejected(multiclienttest_stub):
    multiclienttest_stub.RejectParallelExecution(RejectParallelExecution_Parameters(Duration=Real(value=1)))

    with raises_command_execution_not_accepted_error():
        multiclienttest_stub.RejectParallelExecution(RejectParallelExecution_Parameters(Duration=Real(value=1)))

    time.sleep(1.01)
    multiclienttest_stub.RejectParallelExecution(RejectParallelExecution_Parameters(Duration=Real(value=1)))
