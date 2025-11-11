import uuid

from sila2_interop_communication_tester.grpc_stubs import AuthenticationService_pb2, SiLAFramework_pb2
from sila2_interop_communication_tester.test_client.helpers.error_handling import (
    raises_defined_execution_error,
    raises_validation_error,
)
from sila2_interop_communication_tester.test_client.helpers.sila_service import get_server_uuid

FEATURE = "org.silastandard/core/AuthenticationService/v1"
LOGIN = f"{FEATURE}/Command/Login"


def test_login_fails_on_missing_parameter(authenticationservice_stub, silaservice_stub):
    """Login must reject requests with missing parameters with a Validation Error."""
    # NOTE: RequestedFeatures is a List, so its presence cannot be detected (empty list == no value on wire)
    with raises_validation_error(f"{LOGIN}/Parameter/UserIdentification"):
        authenticationservice_stub.Login(
            AuthenticationService_pb2.Login_Parameters(
                Password=SiLAFramework_pb2.String(value="password"),
                RequestedServer=SiLAFramework_pb2.String(value=get_server_uuid(silaservice_stub)),
                RequestedFeatures=[SiLAFramework_pb2.String(value="org.silastandard/test/AuthenticationTest/v1")],
            )
        )

    with raises_validation_error(f"{LOGIN}/Parameter/Password"):
        authenticationservice_stub.Login(
            AuthenticationService_pb2.Login_Parameters(
                UserIdentification=SiLAFramework_pb2.String(value="username"),
                RequestedServer=SiLAFramework_pb2.String(value=get_server_uuid(silaservice_stub)),
                RequestedFeatures=[SiLAFramework_pb2.String(value="org.silastandard/test/AuthenticationTest/v1")],
            )
        )

    with raises_validation_error(f"{LOGIN}/Parameter/RequestedServer"):
        authenticationservice_stub.Login(
            AuthenticationService_pb2.Login_Parameters(
                UserIdentification=SiLAFramework_pb2.String(value="username"),
                Password=SiLAFramework_pb2.String(value="password"),
                RequestedFeatures=[SiLAFramework_pb2.String(value="org.silastandard/test/AuthenticationTest/v1")],
            )
        )


def test_login_fails_on_invalid_requested_server_uuid(authenticationservice_stub):
    """Login must reject parameter values for RequestedServer that are no UUID strings."""
    with raises_validation_error(f"{LOGIN}/Parameter/RequestedServer"):
        authenticationservice_stub.Login(
            AuthenticationService_pb2.Login_Parameters(
                UserIdentification=SiLAFramework_pb2.String(value="username"),
                Password=SiLAFramework_pb2.String(value="password"),
                RequestedServer=SiLAFramework_pb2.String(value="this-string-is-no-uuid"),
                RequestedFeatures=[SiLAFramework_pb2.String(value="org.silastandard/test/AuthenticationTest/v1")],
            )
        )


def test_login_fails_on_invalid_feature_identifier(authenticationservice_stub, silaservice_stub):
    """Login must reject parameter values for RequestedFeatures that are no fully qualified feature identifiers."""
    with raises_validation_error(f"{LOGIN}/Parameter/RequestedFeatures"):
        authenticationservice_stub.Login(
            AuthenticationService_pb2.Login_Parameters(
                UserIdentification=SiLAFramework_pb2.String(value="username"),
                Password=SiLAFramework_pb2.String(value="password"),
                RequestedServer=SiLAFramework_pb2.String(value=get_server_uuid(silaservice_stub)),
                RequestedFeatures=[SiLAFramework_pb2.String(value="not-a-valid-fully-qualified-feature-identifier")],
            )
        )


def test_login_with_test_test_returns_a_token_and_lifetime(authenticationservice_stub, silaservice_stub):
    login_response = authenticationservice_stub.Login(
        AuthenticationService_pb2.Login_Parameters(
            UserIdentification=SiLAFramework_pb2.String(value="test"),
            Password=SiLAFramework_pb2.String(value="test"),
            RequestedServer=SiLAFramework_pb2.String(value=get_server_uuid(silaservice_stub)),
            RequestedFeatures=[SiLAFramework_pb2.String(value="org.silastandard/test/AuthenticationTest/v1")],
        )
    )

    token = login_response.AccessToken.value
    assert len(token) > 0, "Obtained token was empty"

    lifetime = login_response.TokenLifetime.value
    assert lifetime >= 1, "Obtained token lifetime is less than one second"


def test_logout_fails_on_missing_parameter(authenticationservice_stub):
    with raises_validation_error(f"{FEATURE}/Command/Logout/Parameter/AccessToken"):
        authenticationservice_stub.Logout(AuthenticationService_pb2.Logout_Parameters())


def test_logout_fails_on_unknown_access_token(authenticationservice_stub):
    with raises_defined_execution_error(f"{FEATURE}/DefinedExecutionError/InvalidAccessToken"):
        authenticationservice_stub.Logout(
            AuthenticationService_pb2.Logout_Parameters(AccessToken=SiLAFramework_pb2.String(value=str(uuid.uuid4())))
        )


def test_logout_after_login(authenticationservice_stub, silaservice_stub):
    """Log in with user 'test' and password 'test', log out, expect the token to be invalid afterwards."""
    login_response = authenticationservice_stub.Login(
        AuthenticationService_pb2.Login_Parameters(
            UserIdentification=SiLAFramework_pb2.String(value="test"),
            Password=SiLAFramework_pb2.String(value="test"),
            RequestedServer=SiLAFramework_pb2.String(value=get_server_uuid(silaservice_stub)),
            RequestedFeatures=[SiLAFramework_pb2.String(value="org.silastandard/test/AuthenticationTest/v1")],
        )
    )

    access_token = login_response.AccessToken.value

    authenticationservice_stub.Logout(
        AuthenticationService_pb2.Logout_Parameters(AccessToken=SiLAFramework_pb2.String(value=access_token))
    )

    with raises_defined_execution_error(f"{FEATURE}/DefinedExecutionError/InvalidAccessToken"):
        authenticationservice_stub.Logout(
            AuthenticationService_pb2.Logout_Parameters(AccessToken=SiLAFramework_pb2.String(value=access_token))
        )
