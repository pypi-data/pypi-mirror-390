import uuid

from pytest import fail

from sila2_interop_communication_tester.grpc_stubs import (
    AuthenticationService_pb2,
    AuthenticationTest_pb2,
    AuthorizationService_pb2,
    SiLABinaryTransfer_pb2,
    SiLAFramework_pb2,
)
from sila2_interop_communication_tester.grpc_stubs.AuthenticationService_pb2_grpc import AuthenticationServiceStub
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import DefinedExecutionError, ValidationError
from sila2_interop_communication_tester.grpc_stubs.SiLAService_pb2_grpc import SiLAServiceStub
from sila2_interop_communication_tester.test_client.helpers.binary_transfer import upload_binary
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_defined_execution_error,
    raises_invalid_metadata_error,
    raises_sila_error,
    raises_validation_error,
)
from sila2_interop_communication_tester.test_client.helpers.sila_service import get_server_uuid
from sila2_interop_communication_tester.test_client.helpers.utils import pack_metadata


def log_in(silaservice_stub: SiLAServiceStub, authenticationservice_stub: AuthenticationServiceStub) -> str:
    return authenticationservice_stub.Login(
        AuthenticationService_pb2.Login_Parameters(
            UserIdentification=SiLAFramework_pb2.String(value="test"),
            Password=SiLAFramework_pb2.String(value="test"),
            RequestedServer=SiLAFramework_pb2.String(value=get_server_uuid(silaservice_stub)),
            RequestedFeatures=[SiLAFramework_pb2.String(value="org.silastandard/test/AuthenticationTest/v1")],
        )
    ).AccessToken.value


def test_command_fails_on_missing_token(authenticationtest_stub):
    """
    Request 'RequiresTokenForBinaryUpload' with a small binary, without sending an Access Token.
    Expect an Invalid Metadata error.
    """
    with raises_invalid_metadata_error():
        authenticationtest_stub.RequiresTokenForBinaryUpload(
            AuthenticationTest_pb2.RequiresTokenForBinaryUpload_Parameters(
                BinaryToUpload=SiLAFramework_pb2.Binary(value=b"abcdefg")
            )
        )


def test_command_fails_on_invalid_token(authenticationtest_stub):
    """
    Request 'RequiresTokenForBinaryUpload' with a small binary, with a random (invalid) access token.
    Expect a Defined Execution Error 'Invalid Access Token'.
    """
    with raises_defined_execution_error(
        "org.silastandard/core/AuthorizationService/v1/DefinedExecutionError/InvalidAccessToken"
    ):
        authenticationtest_stub.RequiresTokenForBinaryUpload.with_call(
            request=AuthenticationTest_pb2.RequiresTokenForBinaryUpload_Parameters(
                BinaryToUpload=SiLAFramework_pb2.Binary(value=b"abcdefg")
            ),
            metadata=pack_metadata(
                AuthorizationService_pb2.Metadata_AccessToken(
                    AccessToken=SiLAFramework_pb2.String(value=str(uuid.uuid4()))
                )
            ),
        )


def test_command_fails_on_missing_parameter(authenticationtest_stub, silaservice_stub, authenticationservice_stub):
    """
    Request 'RequiresTokenForBinaryUpload' without a parameter, with a valid access token.
    Expect a Validation Error (missing parameter).
    """
    token = log_in(silaservice_stub, authenticationservice_stub)

    with raises_validation_error(
        "org.silastandard/test/AuthenticationTest/v1/Command/RequiresTokenForBinaryUpload/Parameter/BinaryToUpload"
    ):
        authenticationtest_stub.RequiresTokenForBinaryUpload.with_call(
            request=AuthenticationTest_pb2.RequiresTokenForBinaryUpload_Parameters(),
            metadata=pack_metadata(
                AuthorizationService_pb2.Metadata_AccessToken(AccessToken=SiLAFramework_pb2.String(value=token))
            ),
        )


def test_command_fails_on_invalid_token_and_missing_parameter(authenticationtest_stub):
    """
    Request 'RequiresTokenForBinaryUpload' without a parameter, with a random (invalid) access token.
    Expect a Validation Error (missing parameter) OR a Defined Execution Error 'Invalid Access Token'.

    Note: Metadata-related Execution Errors like 'Invalid Access Token' can occur before or after parameter validation.
    This is an implementation detail of the server.
    """
    with raises_sila_error(["validationError", "definedExecutionError"]) as ex:
        authenticationtest_stub.RequiresTokenForBinaryUpload.with_call(
            request=AuthenticationTest_pb2.RequiresTokenForBinaryUpload_Parameters(),
            metadata=pack_metadata(
                AuthorizationService_pb2.Metadata_AccessToken(
                    AccessToken=SiLAFramework_pb2.String(value=str(uuid.uuid4()))
                )
            ),
        )

    error = ex.error
    if isinstance(error, ValidationError):
        assert (
            error.parameter
            == "org.silastandard/test/AuthenticationTest/v1/Command/RequiresTokenForBinaryUpload/Parameter/BinaryToUpload"
        )
    elif isinstance(error, DefinedExecutionError):
        assert (
            error.errorIdentifier
            == "org.silastandard/core/AuthorizationService/v1/DefinedExecutionError/InvalidAccessToken"
        )
    else:
        fail(f"Expected a defined execution error or validation error, got {error}")


def test_command_works_for_small_binary(authenticationtest_stub, authenticationservice_stub, silaservice_stub):
    """
    Request 'RequiresTokenForBinaryUpload' with a small binary as parameter, with a valid access token.
    Expect a no error.
    """
    token = log_in(silaservice_stub, authenticationservice_stub)

    authenticationtest_stub.RequiresTokenForBinaryUpload.with_call(
        request=AuthenticationTest_pb2.RequiresTokenForBinaryUpload_Parameters(
            BinaryToUpload=SiLAFramework_pb2.Binary(value=b"abc")
        ),
        metadata=pack_metadata(
            AuthorizationService_pb2.Metadata_AccessToken(AccessToken=SiLAFramework_pb2.String(value=token))
        ),
    )


def test_large_binary_parameter_upload_fails_without_token(
    authenticationtest_stub, authenticationservice_stub, silaservice_stub, binary_upload_stub
):
    """
    Request to upload a large binary for the parameter 'Binary To Upload' of the command 'RequiresTokenForBinaryUpload'
    without sending an access token.
    Expect an Invalid Metadata error.
    """
    with raises_invalid_metadata_error():
        binary_upload_stub.CreateBinary(
            SiLABinaryTransfer_pb2.CreateBinaryRequest(
                binarySize=3 * 1024**2,
                chunkCount=3,
                parameterIdentifier=(
                    "org.silastandard/test/AuthenticationTest/v1/Command/RequiresTokenForBinaryUpload/"
                    "Parameter/BinaryToUpload"
                ),
            )
        )


def test_large_binary_parameter_upload_fails_with_invalid_token(
    authenticationtest_stub, authenticationservice_stub, silaservice_stub, binary_upload_stub
):
    """
    Request to upload a large binary for the parameter 'Binary To Upload' of the command 'RequiresTokenForBinaryUpload'
    with sending a random (invalid) access token.
    Expect an Defined Execution Error 'Invalid Access Token'.
    """
    with raises_defined_execution_error(
        "org.silastandard/core/AuthorizationService/v1/DefinedExecutionError/InvalidAccessToken"
    ):
        binary_upload_stub.CreateBinary.with_call(
            request=SiLABinaryTransfer_pb2.CreateBinaryRequest(
                binarySize=3 * 1024**2,
                chunkCount=3,
                parameterIdentifier=(
                    "org.silastandard/test/AuthenticationTest/v1/Command/RequiresTokenForBinaryUpload/"
                    "Parameter/BinaryToUpload"
                ),
            ),
            metadata=pack_metadata(
                AuthorizationService_pb2.Metadata_AccessToken(
                    AccessToken=SiLAFramework_pb2.String(value=str(uuid.uuid4()))
                )
            ),
        )


def test_command_works_for_large_binary_without_metadata_during_binary_upload(
    authenticationtest_stub, authenticationservice_stub, silaservice_stub, binary_upload_stub
):
    """
    Request to upload a large binary for the parameter 'Binary To Upload' of the command 'RequiresTokenForBinaryUpload'
    with sending a valid access token.
    Then call the command using the uploaded binary.
    Expect no error.
    """
    token = log_in(silaservice_stub, authenticationservice_stub)

    binary_uuid = upload_binary(
        binary_upload_stub,
        b"abc" * 1_000_000,
        "org.silastandard/test/AuthenticationTest/v1/Command/RequiresTokenForBinaryUpload/Parameter/BinaryToUpload",
        metadata=[AuthorizationService_pb2.Metadata_AccessToken(AccessToken=SiLAFramework_pb2.String(value=token))],
    )

    authenticationtest_stub.RequiresTokenForBinaryUpload.with_call(
        request=AuthenticationTest_pb2.RequiresTokenForBinaryUpload_Parameters(
            BinaryToUpload=SiLAFramework_pb2.Binary(binaryTransferUUID=str(binary_uuid))
        ),
        metadata=pack_metadata(
            AuthorizationService_pb2.Metadata_AccessToken(AccessToken=SiLAFramework_pb2.String(value=token))
        ),
    )
