import time
import uuid
from datetime import datetime

from sila2_interop_communication_tester.grpc_stubs.MultiClientTest_pb2 import (
    RunInParallel_Parameters,
    RunInParallel_Responses,
)
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import (
    CommandExecutionUUID,
    ExecutionInfo,
    Integer,
    Real,
)
from sila2_interop_communication_tester.helpers.utils import string_is_uuid
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_command_execution_not_finished_error,
    raises_invalid_command_execution_uuid_error,
    raises_validation_error,
)


def test_rejects_missing_parameter(multiclienttest_stub):
    with raises_validation_error("org.silastandard/test/MultiClientTest/v1/Command/RunInParallel/Parameter/Duration"):
        multiclienttest_stub.RunInParallel(RunInParallel_Parameters())


def test_info_rejects_non_uuid_strings(multiclienttest_stub):
    stream = multiclienttest_stub.RunInParallel_Info(CommandExecutionUUID(value="abcde"))
    with raises_invalid_command_execution_uuid_error():
        next(stream)


def test_info_rejects_unknown_uuids(multiclienttest_stub):
    stream = multiclienttest_stub.RunInParallel_Info(CommandExecutionUUID(value=str(uuid.uuid4())))
    with raises_invalid_command_execution_uuid_error():
        next(stream)


def test_result_rejects_non_uuid_strings(multiclienttest_stub):
    with raises_invalid_command_execution_uuid_error():
        multiclienttest_stub.RunInParallel_Result(CommandExecutionUUID(value="abcde"))


def test_result_rejects_unknown_uuids(multiclienttest_stub):
    with raises_invalid_command_execution_uuid_error():
        multiclienttest_stub.RunInParallel_Result(CommandExecutionUUID(value=str(uuid.uuid4())))


def test_returns_valid_uuid(multiclienttest_stub):
    exec_info = multiclienttest_stub.RunInParallel(RunInParallel_Parameters(Duration=Real(value=0.1)))
    assert string_is_uuid(exec_info.commandExecutionUUID.value)


def test_result_raises_command_execution_not_finished(multiclienttest_stub):
    exec_info = multiclienttest_stub.RunInParallel(RunInParallel_Parameters(Duration=Real(value=0.1)))

    with raises_command_execution_not_finished_error():
        multiclienttest_stub.RunInParallel_Result(exec_info.commandExecutionUUID)


def test_info_reports_success_when_subscribing_after_command_finished(multiclienttest_stub):
    exec_info = multiclienttest_stub.RunInParallel(RunInParallel_Parameters(Duration=Real(value=0.1)))
    time.sleep(0.15)  # wait until command finishes

    info_stream = multiclienttest_stub.RunInParallel_Info(exec_info.commandExecutionUUID)
    infos = list(info_stream)
    assert infos, "Client did not receive execution information when subscribing after command finished"
    assert all(info.commandStatus == ExecutionInfo.CommandStatus.finishedSuccessfully for info in infos)


def test_parallel_execution_works(multiclienttest_stub):
    start_timestamp = datetime.now()
    exec1_info = multiclienttest_stub.RunInParallel(RunInParallel_Parameters(Duration=Real(value=1)))
    exec2_info = multiclienttest_stub.RunInParallel(RunInParallel_Parameters(Duration=Real(value=1)))

    time.sleep(0.05)

    info1_stream = multiclienttest_stub.RunInParallel_Info(exec1_info.commandExecutionUUID)
    info2_stream = multiclienttest_stub.RunInParallel_Info(exec2_info.commandExecutionUUID)

    # block until streams end: wait until commands finish
    infos1 = list(info1_stream)
    infos2 = list(info2_stream)
    assert 1 < (datetime.now() - start_timestamp).total_seconds() < 1.5

    assert multiclienttest_stub.RunInParallel_Result(exec1_info.commandExecutionUUID) == RunInParallel_Responses()
    assert multiclienttest_stub.RunInParallel_Result(exec2_info.commandExecutionUUID) == RunInParallel_Responses()

    assert infos1[0].commandStatus == ExecutionInfo.CommandStatus.running
    assert infos1[-1].commandStatus == ExecutionInfo.CommandStatus.finishedSuccessfully
    assert infos2[0].commandStatus == ExecutionInfo.CommandStatus.running
    assert infos2[-1].commandStatus == ExecutionInfo.CommandStatus.finishedSuccessfully
