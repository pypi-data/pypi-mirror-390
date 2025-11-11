import uuid

from sila2_interop_communication_tester.grpc_stubs import (
    AuthenticationService_pb2,
    AuthenticationTest_pb2,
    AuthorizationService_pb2,
    SiLAFramework_pb2,
)
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_defined_execution_error,
    raises_invalid_metadata_error,
)
from sila2_interop_communication_tester.test_client.helpers.sila_service import get_server_uuid
from sila2_interop_communication_tester.test_client.helpers.utils import pack_metadata


def test_command_fails_on_missing_token(authenticationtest_stub):
    """Command 'RequiresToken' must fail with an Invalid Metadata Error if no token is sent."""
    with raises_invalid_metadata_error():
        authenticationtest_stub.RequiresToken(AuthenticationTest_pb2.RequiresToken_Parameters())


def test_command_fails_on_invalid_token(authenticationtest_stub):
    """Command 'RequiresToken' must fail with 'AuthorizationService.InvalidAccessToken' if a random token is sent."""
    with raises_defined_execution_error(
        "org.silastandard/core/AuthorizationService/v1/DefinedExecutionError/InvalidAccessToken"
    ):
        authenticationtest_stub.RequiresToken.with_call(
            request=AuthenticationTest_pb2.RequiresToken_Parameters(),
            metadata=pack_metadata(
                AuthorizationService_pb2.Metadata_AccessToken(
                    AccessToken=SiLAFramework_pb2.String(value=str(uuid.uuid4()))
                )
            ),
        )


def test_command_works(authenticationtest_stub, authenticationservice_stub, silaservice_stub):
    login_response = authenticationservice_stub.Login(
        AuthenticationService_pb2.Login_Parameters(
            UserIdentification=SiLAFramework_pb2.String(value="test"),
            Password=SiLAFramework_pb2.String(value="test"),
            RequestedServer=SiLAFramework_pb2.String(value=get_server_uuid(silaservice_stub)),
            RequestedFeatures=[SiLAFramework_pb2.String(value="org.silastandard/test/AuthenticationTest/v1")],
        )
    )

    authenticationtest_stub.RequiresToken.with_call(
        request=AuthenticationTest_pb2.RequiresToken_Parameters(),
        metadata=pack_metadata(AuthorizationService_pb2.Metadata_AccessToken(AccessToken=login_response.AccessToken)),
    )
