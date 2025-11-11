import time
import uuid
from datetime import datetime

from sila2_interop_communication_tester.grpc_stubs.MultiClientTest_pb2 import RunQueued_Parameters, RunQueued_Responses
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import CommandExecutionUUID, ExecutionInfo, Real
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_command_execution_not_finished_error,
    raises_invalid_command_execution_uuid_error,
    raises_validation_error,
)


def test_rejects_missing_parameter(multiclienttest_stub):
    with raises_validation_error("org.silastandard/test/MultiClientTest/v1/Command/RunQueued/Parameter/Duration"):
        multiclienttest_stub.RunQueued(RunQueued_Parameters())


def test_info_rejects_non_uuid_strings(multiclienttest_stub):
    stream = multiclienttest_stub.RunQueued_Info(CommandExecutionUUID(value="abcde"))
    with raises_invalid_command_execution_uuid_error():
        next(stream)


def test_info_rejects_unknown_uuids(multiclienttest_stub):
    stream = multiclienttest_stub.RunQueued_Info(CommandExecutionUUID(value=str(uuid.uuid4())))
    with raises_invalid_command_execution_uuid_error():
        next(stream)


def test_result_rejects_non_uuid_strings(multiclienttest_stub):
    with raises_invalid_command_execution_uuid_error():
        multiclienttest_stub.RunQueued_Result(CommandExecutionUUID(value="abcde"))


def test_result_rejects_unknown_uuids(multiclienttest_stub):
    with raises_invalid_command_execution_uuid_error():
        multiclienttest_stub.RunQueued_Result(CommandExecutionUUID(value=str(uuid.uuid4())))


def test_queued_execution_works(multiclienttest_stub):
    start_timestamp = datetime.now()
    exec1_info = multiclienttest_stub.RunQueued(RunQueued_Parameters(Duration=Real(value=1)))
    exec2_info = multiclienttest_stub.RunQueued(RunQueued_Parameters(Duration=Real(value=1)))

    time.sleep(0.05)

    info1_stream = multiclienttest_stub.RunQueued_Info(exec1_info.commandExecutionUUID)
    info2_stream = multiclienttest_stub.RunQueued_Info(exec2_info.commandExecutionUUID)

    assert next(info1_stream).commandStatus == ExecutionInfo.CommandStatus.running
    assert next(info2_stream).commandStatus == ExecutionInfo.CommandStatus.waiting

    with raises_command_execution_not_finished_error():
        multiclienttest_stub.RunQueued_Result(exec1_info.commandExecutionUUID)
    with raises_command_execution_not_finished_error():
        multiclienttest_stub.RunQueued_Result(exec2_info.commandExecutionUUID)

    # block until streams end: wait until commands finish
    infos1 = list(info1_stream)
    infos2 = list(info2_stream)
    assert 2 < (datetime.now() - start_timestamp).total_seconds() < 2.5

    assert multiclienttest_stub.RunQueued_Result(exec1_info.commandExecutionUUID) == RunQueued_Responses()
    assert multiclienttest_stub.RunQueued_Result(exec2_info.commandExecutionUUID) == RunQueued_Responses()

    assert infos1[-1].commandStatus == ExecutionInfo.CommandStatus.finishedSuccessfully
    assert infos2[0].commandStatus == ExecutionInfo.CommandStatus.running
    assert infos2[-1].commandStatus == ExecutionInfo.CommandStatus.finishedSuccessfully
