from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING
from uuid import UUID

import grpc

from sila2_interop_communication_tester.grpc_stubs import AuthenticationService_pb2, SiLAFramework_pb2
from sila2_interop_communication_tester.grpc_stubs.AuthenticationService_pb2_grpc import AuthenticationServiceServicer
from sila2_interop_communication_tester.test_server.helpers.raise_error import (
    raise_defined_execution_error,
    raise_validation_error,
)

if TYPE_CHECKING:
    from sila2_interop_communication_tester.test_server.server_implementation.server import ServerState


class AuthenticationServiceImpl(AuthenticationServiceServicer):
    def __init__(self, server_state: ServerState):
        self.server_state = server_state

    def Login(
        self, request: AuthenticationService_pb2.Login_Parameters, context: grpc.ServicerContext
    ) -> AuthenticationService_pb2.Login_Responses:
        for param_id in ["UserIdentification", "Password", "RequestedServer"]:
            if not request.HasField(param_id):
                raise_validation_error(
                    context,
                    f"org.silastandard/core/AuthenticationService/v1/Command/Login/Parameter/{param_id}",
                    f"Missing parameter '{param_id}'",
                )
        if not re.fullmatch(
            "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", request.RequestedServer.value
        ):
            raise_validation_error(
                context,
                "org.silastandard/core/AuthenticationService/v1/Command/Login/Parameter/RequestedServer",
                f"Parameter 'RequestedServer' does not match pattern "
                f"'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', "
                f"was {request.RequestedServer.value!r}",
            )
        requested_features = [f.value for f in request.RequestedFeatures]
        for feature in requested_features:
            if not re.fullmatch(r"[a-z][a-z.]*/[a-z][a-z.]*/[A-Z][a-zA-Z0-9]*/v\d+", feature):
                raise_validation_error(
                    context,
                    "org.silastandard/core/AuthenticationService/v1/Command/Login/Parameter/RequestedFeatures",
                    f"'Requested Feature' parameter is not a fully qualified feature identifier: {feature}",
                )

        if UUID(request.RequestedServer.value) != self.server_state.server_uuid:
            raise_defined_execution_error(
                context,
                "org.silastandard/core/AuthenticationService/v1/DefinedExecutionError/AuthenticationFailed",
                f"Unknown server UUID: {request.RequestedServer.value!r}",
            )

        if requested_features != ["org.silastandard/test/AuthenticationTest/v1"]:
            raise_defined_execution_error(
                context,
                "org.silastandard/core/AuthenticationService/v1/DefinedExecutionError/AuthenticationFailed",
                f"Login is only possible for the 'Authentication Test' feature, not {requested_features!r}",
            )

        if request.UserIdentification.value != "test" or request.Password.value != "test":
            raise_defined_execution_error(
                context,
                "org.silastandard/core/AuthenticationService/v1/DefinedExecutionError/AuthenticationFailed",
                "Invalid credentials",
            )

        token = str(uuid.uuid4())
        lifetime_seconds = 60 * 10  # 10 minutes

        self.server_state.auth_tokens[token] = datetime.now() + timedelta(seconds=lifetime_seconds)
        return AuthenticationService_pb2.Login_Responses(
            AccessToken=SiLAFramework_pb2.String(value=str(token)),
            TokenLifetime=SiLAFramework_pb2.Integer(value=lifetime_seconds),
        )

    def Logout(
        self, request: AuthenticationService_pb2.Logout_Parameters, context: grpc.ServicerContext
    ) -> AuthenticationService_pb2.Logout_Responses:
        if not request.HasField("AccessToken"):
            raise_validation_error(
                context,
                "org.silastandard/core/AuthenticationService/v1/Command/Logout/Parameter/AccessToken",
                "Missing parameter 'AccessToken'",
            )

        if (
            request.AccessToken.value not in self.server_state.auth_tokens
            or self.server_state.auth_tokens[request.AccessToken.value] < datetime.now()
        ):
            raise_defined_execution_error(
                context,
                "org.silastandard/core/AuthenticationService/v1/DefinedExecutionError/InvalidAccessToken",
                "Invalid access token",
            )

        self.server_state.auth_tokens.pop(request.AccessToken.value)

        return AuthenticationService_pb2.Logout_Responses()
