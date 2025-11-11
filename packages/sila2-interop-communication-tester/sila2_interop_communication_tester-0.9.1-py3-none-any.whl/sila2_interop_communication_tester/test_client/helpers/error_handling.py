"""Defines context managers to assert that SiLA Errors are raised"""
import binascii
import re
from base64 import standard_b64decode
from types import TracebackType
from typing import Callable, Collection, Generic, Literal, Optional, Type, TypeVar, Union

import google.protobuf.message
import grpc
from pytest import fail

from sila2_interop_communication_tester.grpc_stubs.SiLABinaryTransfer_pb2 import BinaryTransferError
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import (
    DefinedExecutionError,
    FrameworkError,
    SiLAError,
    UndefinedExecutionError,
    ValidationError,
)

_ErrorType = TypeVar(
    "_ErrorType", ValidationError, FrameworkError, DefinedExecutionError, UndefinedExecutionError, BinaryTransferError
)
_ErrorTypeName = Literal["validationError", "frameworkError", "definedExecutionError", "undefinedExecutionError"]
_FrameworkErrorType = Literal[
    "COMMAND_EXECUTION_NOT_ACCEPTED",
    "INVALID_COMMAND_EXECUTION_UUID",
    "COMMAND_EXECUTION_NOT_FINISHED",
    "INVALID_METADATA",
    "NO_METADATA_ALLOWED",
]
_BinaryTransferErrorType = Literal[
    "BINARY_UPLOAD_FAILED",
    "BINARY_DOWNLOAD_FAILED",
    "INVALID_BINARY_TRANSFER_UUID",
]
_ERROR_MESSAGE_TYPE = Union[Type[SiLAError], Type[BinaryTransferError]]
_ERROR_MESSAGE = Union[SiLAError, BinaryTransferError]


def check_error_message(error_message: str) -> None:
    assert (
        len(error_message) > 10
    ), "Error message was less than 10 characters long (SiLA Errors must include information about the error)"


def parse_error_from_exception(
    error_message_cls: _ERROR_MESSAGE_TYPE,
    exception: BaseException,
) -> Optional[_ERROR_MESSAGE]:
    assert isinstance(exception, grpc.RpcError), "Caught a non-gRPC error (probably an internal error in test suite)"
    assert isinstance(exception, grpc.Call), "Caught a non-gRPC error (probably an internal error in test suite)"
    assert (
        exception.code() == grpc.StatusCode.ABORTED
    ), f"Caught gRPC error with wrong status code (expected {grpc.StatusCode.ABORTED}, got {exception.code()})"

    try:
        proto_bytes = standard_b64decode(exception.details())
    except binascii.Error:
        fail("Failed to decode error details as Base64")
        return

    try:
        return error_message_cls.FromString(proto_bytes)
    except google.protobuf.message.DecodeError:
        fail("Failed to decode error details as SiLAFramework.SiLAError Protobuf message")
        return


class ErrorOption(Generic[_ErrorType]):
    def __init__(self):
        self.error: Optional[_ErrorType] = None


class RaisesContext(Generic[_ErrorType]):
    # adapted from pytest.raises
    def __init__(
        self,
        error_message_cls: _ERROR_MESSAGE_TYPE,
        *,
        expected_error_types: Optional[Collection[_ErrorTypeName]] = None,
        check_func: Optional[Callable[[_ErrorType], None]] = None,
    ) -> None:
        self.expected_error_types = expected_error_types
        self.error_option: ErrorOption[_ErrorType] = ErrorOption()
        self.check_func: Optional[Callable[[_ErrorType], None]] = check_func
        self.error_message_cls = error_message_cls

    def __enter__(self) -> ErrorOption[_ErrorType]:
        return self.error_option

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> Optional[bool]:
        __tracebackhide__ = True

        if exc_type is None:
            fail("Expected a gRPC error, but no exception was caught")
        if not issubclass(exc_type, grpc.RpcError):
            return False
        error = parse_error_from_exception(self.error_message_cls, exc_val)
        if error is None:
            return False

        if isinstance(error, BinaryTransferError):
            check_error_message(error.message)
        else:
            sila_error_type_name = error.WhichOneof("error")
            if sila_error_type_name is None:
                fail("SiLAError message contained no 'error'")
            if sila_error_type_name not in self.expected_error_types:
                fail(
                    "Caught SiLA Error of wrong type "
                    f"(expected one of '{self.expected_error_types}', got '{sila_error_type_name}')"
                )
            error = getattr(error, sila_error_type_name)
            check_error_message(error.message)

        if self.check_func is not None:
            self.check_func(error)

        self.error_option.error = error
        return True


def raises_sila_error(expected_error_types: Collection[_ErrorTypeName]) -> RaisesContext[SiLAError]:
    return RaisesContext(SiLAError, expected_error_types=expected_error_types)


def raises_defined_execution_error(error_identifier: str) -> RaisesContext[DefinedExecutionError]:
    """
    Equivalent to `pytest.raises` for a SiLA Defined Execution Error with the given fully qualified error identifier
    """

    def check_func(error: DefinedExecutionError) -> None:
        assert error.errorIdentifier == error_identifier, (
            f"Caught DefinedExecutionError with wrong errorIdentifier "
            f"(expected '{error_identifier}', got '{error.errorIdentifier}')"
        )

    return RaisesContext(SiLAError, expected_error_types=["definedExecutionError"], check_func=check_func)


def raises_undefined_execution_error() -> RaisesContext[UndefinedExecutionError]:
    """Equivalent to `pytest.raises` for a SiLA Undefined Execution Error"""
    return RaisesContext(SiLAError, expected_error_types=["undefinedExecutionError"])


def raises_validation_error(parameter_identifier_regex: str) -> RaisesContext[ValidationError]:
    """
    Equivalent to `pytest.raises` for a SiLA Validation Error with a fully qualified parameter identifier
    matching the given pattern
    """

    def check_func(error: ValidationError) -> None:
        assert re.fullmatch(parameter_identifier_regex, error.parameter), (
            f"Caught ValidationError for wrong parameter "
            f"(expected '{parameter_identifier_regex}', got '{error.parameter}')"
        )

    return RaisesContext(SiLAError, expected_error_types=["validationError"], check_func=check_func)


def __raises_framework_error(error_type: _FrameworkErrorType) -> RaisesContext[FrameworkError]:
    error_type = getattr(FrameworkError.ErrorType, error_type)

    def check_func(error: FrameworkError) -> None:
        assert (
            error.errorType == error_type
        ), f"Caught FrameworkError with wrong errorType (expected '{error_type}', got '{error.errorType}')"

    return RaisesContext(SiLAError, expected_error_types=["frameworkError"], check_func=check_func)


def raises_command_execution_not_accepted_error():
    """Equivalent to `pytest.raises` for a SiLA Command Execution Not Accepted Error"""
    return __raises_framework_error("COMMAND_EXECUTION_NOT_ACCEPTED")


def raises_invalid_command_execution_uuid_error():
    """Equivalent to `pytest.raises` for a SiLA Invalid Command Execution UUID Error"""
    return __raises_framework_error("INVALID_COMMAND_EXECUTION_UUID")


def raises_command_execution_not_finished_error():
    """Equivalent to `pytest.raises` for a SiLA Command Execution Not Finished Error"""
    return __raises_framework_error("COMMAND_EXECUTION_NOT_FINISHED")


def raises_invalid_metadata_error():
    """Equivalent to `pytest.raises` for a SiLA Invalid Metadata Error"""
    return __raises_framework_error("INVALID_METADATA")


def raises_no_metadata_allowed_error():
    """Equivalent to `pytest.raises` for a SiLA No Metadata Allowed Error"""
    return __raises_framework_error("NO_METADATA_ALLOWED")


def __raises_binary_transfer_error(error_type: _BinaryTransferErrorType) -> RaisesContext[BinaryTransferError]:
    error_type = getattr(BinaryTransferError.ErrorType, error_type)

    def check_func(error: BinaryTransferError) -> None:
        assert error.errorType == error_type, (
            f"Caught BinaryTransferError with wrong errorType "
            f"(expected '{BinaryTransferError.ErrorType.Name(error_type)}', "
            f"got '{BinaryTransferError.ErrorType.Name(error.errorType)}')"
        )

    return RaisesContext(BinaryTransferError, check_func=check_func)


def raises_binary_upload_failed_error():
    """Equivalent to `pytest.raises` for a SiLA Binary Upload Failed Error"""
    return __raises_binary_transfer_error("BINARY_UPLOAD_FAILED")


def raises_binary_download_failed_error():
    """Equivalent to `pytest.raises` for a SiLA Binary Download Failed Error"""
    return __raises_binary_transfer_error("BINARY_DOWNLOAD_FAILED")


def raises_invalid_binary_transfer_uuid_error():
    """Equivalent to `pytest.raises` for a SiLA Invalid Binary Transfer UUID Error"""
    return __raises_binary_transfer_error("INVALID_BINARY_TRANSFER_UUID")
