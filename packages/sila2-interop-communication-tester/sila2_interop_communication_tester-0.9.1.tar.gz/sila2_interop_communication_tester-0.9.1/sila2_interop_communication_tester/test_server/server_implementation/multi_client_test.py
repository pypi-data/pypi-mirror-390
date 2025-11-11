import collections.abc
import dataclasses
import threading
import time
import uuid
from datetime import datetime, timedelta
from uuid import UUID

import grpc

from sila2_interop_communication_tester.grpc_stubs import MultiClientTest_pb2, SiLAFramework_pb2
from sila2_interop_communication_tester.grpc_stubs.MultiClientTest_pb2_grpc import MultiClientTestServicer
from sila2_interop_communication_tester.helpers.utils import string_is_uuid
from sila2_interop_communication_tester.test_server.helpers.protobuf import duration_from_seconds
from sila2_interop_communication_tester.test_server.helpers.raise_error import (
    raise_command_execution_not_accepted_error,
    raise_command_execution_not_finished_error,
    raise_invalid_command_execution_uuid_error,
    raise_validation_error,
)


@dataclasses.dataclass
class Period:
    start: datetime
    end: datetime

    @property
    def is_running(self) -> bool:
        return self.start < datetime.now() < self.end

    @property
    def is_waiting(self) -> bool:
        return self.start > datetime.now()

    @property
    def is_done(self) -> bool:
        return datetime.now() > self.end

    @property
    def remaining_seconds(self) -> float:
        if self.is_done:
            return 0
        return (self.end - datetime.now()).total_seconds()


class MultiClientTestImpl(MultiClientTestServicer):
    def __init__(self):
        self.run_in_parallel_instances: dict[UUID, Period] = {}

        self.run_queued_registration_lock = threading.Lock()
        self.run_queued_instances: dict[UUID, Period] = {}
        self.run_queued_queue: list[Period] = []

        self.reject_parallel_execution_lock = threading.Lock()
        self.reject_parallel_execution_end = datetime.now()
        self.reject_parallel_execution_instances: dict[UUID, Period] = {}

    def RunInParallel(
        self, request: MultiClientTest_pb2.RunInParallel_Parameters, context: grpc.ServicerContext
    ) -> SiLAFramework_pb2.CommandConfirmation:
        if not request.HasField("Duration"):
            raise_validation_error(
                context,
                "org.silastandard/test/MultiClientTest/v1/Command/RunInParallel/Parameter/Duration",
                "Missing parameter 'Duration'",
            )

        command_id = uuid.uuid4()
        duration = request.Duration.value
        now = datetime.now()
        self.run_in_parallel_instances[command_id] = Period(now, now + timedelta(seconds=duration))
        return SiLAFramework_pb2.CommandConfirmation(
            commandExecutionUUID=SiLAFramework_pb2.CommandExecutionUUID(value=str(command_id))
        )

    def RunInParallel_Info(
        self, request: SiLAFramework_pb2.CommandExecutionUUID, context: grpc.ServicerContext
    ) -> collections.abc.Iterator[SiLAFramework_pb2.ExecutionInfo]:
        if not string_is_uuid(request.value):
            raise_invalid_command_execution_uuid_error(context, f"String is not a valid UUID: '{request.value}'")
        if uuid.UUID(request.value) not in self.run_in_parallel_instances:
            raise_invalid_command_execution_uuid_error(context, f"No command instance with UUID {request.value}")

        instance = self.run_in_parallel_instances[UUID(request.value)]
        if instance.start > datetime.now():
            yield SiLAFramework_pb2.ExecutionInfo(
                progressInfo=SiLAFramework_pb2.Real(value=0),
                commandStatus=SiLAFramework_pb2.ExecutionInfo.CommandStatus.waiting,
                estimatedRemainingTime=duration_from_seconds((instance.end - datetime.now()).total_seconds()),
            )
        while instance.is_running:
            yield SiLAFramework_pb2.ExecutionInfo(
                commandStatus=SiLAFramework_pb2.ExecutionInfo.CommandStatus.running,
                estimatedRemainingTime=duration_from_seconds(instance.remaining_seconds),
            )
            time.sleep(min(1.0, instance.remaining_seconds))
        yield SiLAFramework_pb2.ExecutionInfo(
            progressInfo=SiLAFramework_pb2.Real(value=1),
            commandStatus=SiLAFramework_pb2.ExecutionInfo.CommandStatus.finishedSuccessfully,
            estimatedRemainingTime=duration_from_seconds(instance.remaining_seconds),
        )

    def RunInParallel_Result(
        self, request: SiLAFramework_pb2.CommandExecutionUUID, context: grpc.ServicerContext
    ) -> MultiClientTest_pb2.RunInParallel_Responses:
        if not string_is_uuid(request.value):
            raise_invalid_command_execution_uuid_error(context, f"String is not a valid UUID: '{request.value}'")
        if uuid.UUID(request.value) not in self.run_in_parallel_instances:
            raise_invalid_command_execution_uuid_error(context, f"No command instance with UUID {request.value}")

        instance = self.run_in_parallel_instances[uuid.UUID(request.value)]
        if not instance.is_done:
            raise_command_execution_not_finished_error(context, "Command is still running")
        return MultiClientTest_pb2.RunInParallel_Responses()

    def RunQueued(
        self, request: MultiClientTest_pb2.RunQueued_Parameters, context: grpc.ServicerContext
    ) -> SiLAFramework_pb2.CommandConfirmation:
        if not request.HasField("Duration"):
            raise_validation_error(
                context,
                "org.silastandard/test/MultiClientTest/v1/Command/RunQueued/Parameter/Duration",
                "Missing parameter 'Duration'",
            )

        command_id = uuid.uuid4()
        duration = request.Duration.value
        with self.run_queued_registration_lock:
            start = datetime.now()
            if self.run_queued_instances:
                last_instance = self.run_queued_queue[-1]
                if not last_instance.is_done:
                    start = last_instance.end

            instance = Period(start, start + timedelta(seconds=duration))
            self.run_queued_queue.append(instance)
            self.run_queued_instances[command_id] = instance

        return SiLAFramework_pb2.CommandConfirmation(
            commandExecutionUUID=SiLAFramework_pb2.CommandExecutionUUID(value=str(command_id))
        )

    def RunQueued_Info(
        self, request: SiLAFramework_pb2.CommandExecutionUUID, context: grpc.ServicerContext
    ) -> collections.abc.Iterator[SiLAFramework_pb2.ExecutionInfo]:
        if not string_is_uuid(request.value):
            raise_invalid_command_execution_uuid_error(context, f"String is not a valid UUID: '{request.value}'")
        if uuid.UUID(request.value) not in self.run_queued_instances:
            raise_invalid_command_execution_uuid_error(context, f"No command instance with UUID {request.value}")

        instance = self.run_queued_instances[UUID(request.value)]
        if instance.is_waiting:
            yield SiLAFramework_pb2.ExecutionInfo(
                progressInfo=SiLAFramework_pb2.Real(value=0),
                commandStatus=SiLAFramework_pb2.ExecutionInfo.CommandStatus.waiting,
                estimatedRemainingTime=duration_from_seconds((instance.end - datetime.now()).total_seconds()),
            )
            time.sleep((instance.start - datetime.now()).total_seconds())

        while instance.is_running:
            yield SiLAFramework_pb2.ExecutionInfo(
                commandStatus=SiLAFramework_pb2.ExecutionInfo.CommandStatus.running,
                estimatedRemainingTime=duration_from_seconds(instance.remaining_seconds),
            )
            time.sleep(min(1.0, instance.remaining_seconds))

        yield SiLAFramework_pb2.ExecutionInfo(
            progressInfo=SiLAFramework_pb2.Real(value=1),
            commandStatus=SiLAFramework_pb2.ExecutionInfo.CommandStatus.finishedSuccessfully,
            estimatedRemainingTime=duration_from_seconds(instance.remaining_seconds),
        )

    def RunQueued_Result(
        self, request: SiLAFramework_pb2.CommandExecutionUUID, context: grpc.ServicerContext
    ) -> MultiClientTest_pb2.RunQueued_Responses:
        if not string_is_uuid(request.value):
            raise_invalid_command_execution_uuid_error(context, f"String is not a valid UUID: '{request.value}'")
        if uuid.UUID(request.value) not in self.run_queued_instances:
            raise_invalid_command_execution_uuid_error(context, f"No command instance with UUID {request.value}")

        instance = self.run_queued_instances[uuid.UUID(request.value)]
        if not instance.is_done:
            raise_command_execution_not_finished_error(context, "Command is still running")
        return MultiClientTest_pb2.RunQueued_Responses()

    def RejectParallelExecution(
        self, request: MultiClientTest_pb2.RejectParallelExecution_Parameters, context: grpc.ServicerContext
    ) -> SiLAFramework_pb2.CommandConfirmation:
        if not request.HasField("Duration"):
            raise_validation_error(
                context,
                "org.silastandard/test/MultiClientTest/v1/Command/RejectParallelExecution/Parameter/Duration",
                "Missing parameter 'Duration'",
            )

        with self.reject_parallel_execution_lock:
            now = datetime.now()

            if self.reject_parallel_execution_end > now:
                raise_command_execution_not_accepted_error(
                    context,
                    "Another instance of this command is already running",
                )

            duration = request.Duration.value
            command_id = uuid.uuid4()
            end = now + timedelta(seconds=duration)
            self.reject_parallel_execution_end = end
            self.reject_parallel_execution_instances[command_id] = Period(now, end)

        return SiLAFramework_pb2.CommandConfirmation(
            commandExecutionUUID=SiLAFramework_pb2.CommandExecutionUUID(value=str(command_id))
        )

    def RejectParallelExecution_Info(
        self, request: SiLAFramework_pb2.CommandExecutionUUID, context: grpc.ServicerContext
    ) -> collections.abc.Iterator[SiLAFramework_pb2.ExecutionInfo]:
        if not string_is_uuid(request.value):
            raise_invalid_command_execution_uuid_error(context, f"String is not a valid UUID: '{request.value}'")
        if uuid.UUID(request.value) not in self.run_queued_instances:
            raise_invalid_command_execution_uuid_error(context, f"No command instance with UUID {request.value}")

        instance = self.reject_parallel_execution_instances[UUID(request.value)]
        if instance.start > datetime.now():
            yield SiLAFramework_pb2.ExecutionInfo(
                progressInfo=SiLAFramework_pb2.Real(value=0),
                commandStatus=SiLAFramework_pb2.ExecutionInfo.CommandStatus.waiting,
                estimatedRemainingTime=duration_from_seconds((instance.end - datetime.now()).total_seconds()),
            )
        while instance.is_running:
            yield SiLAFramework_pb2.ExecutionInfo(
                commandStatus=SiLAFramework_pb2.ExecutionInfo.CommandStatus.running,
                estimatedRemainingTime=duration_from_seconds(instance.remaining_seconds),
            )
            time.sleep(min(1.0, instance.remaining_seconds))
        yield SiLAFramework_pb2.ExecutionInfo(
            progressInfo=SiLAFramework_pb2.Real(value=1),
            commandStatus=SiLAFramework_pb2.ExecutionInfo.CommandStatus.finishedSuccessfully,
            estimatedRemainingTime=duration_from_seconds(instance.remaining_seconds),
        )

    def RejectParallelExecution_Result(
        self, request: SiLAFramework_pb2.CommandExecutionUUID, context: grpc.ServicerContext
    ) -> MultiClientTest_pb2.RejectParallelExecution_Responses:
        if not string_is_uuid(request.value):
            raise_invalid_command_execution_uuid_error(context, f"String is not a valid UUID: '{request.value}'")
        if uuid.UUID(request.value) not in self.reject_parallel_execution_instances:
            raise_invalid_command_execution_uuid_error(context, f"No command instance with UUID {request.value}")

        instance = self.reject_parallel_execution_instances[uuid.UUID(request.value)]
        if not instance.is_done:
            raise_command_execution_not_finished_error(context, "Command is still running")
        return MultiClientTest_pb2.RunInParallel_Responses()
