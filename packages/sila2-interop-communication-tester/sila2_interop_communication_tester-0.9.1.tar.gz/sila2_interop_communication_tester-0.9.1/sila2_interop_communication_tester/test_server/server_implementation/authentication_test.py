from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import grpc

from sila2_interop_communication_tester.grpc_stubs import AuthenticationTest_pb2, AuthorizationService_pb2
from sila2_interop_communication_tester.grpc_stubs.AuthenticationTest_pb2_grpc import AuthenticationTestServicer
from sila2_interop_communication_tester.grpc_stubs.AuthorizationService_pb2 import Metadata_AccessToken
from sila2_interop_communication_tester.test_server.helpers.binary_transfer import get_binary
from sila2_interop_communication_tester.test_server.helpers.raise_error import (
    raise_defined_execution_error,
    raise_invalid_metadata_error,
    raise_validation_error,
)
from sila2_interop_communication_tester.test_server.helpers.spy import MetadataDict, extract_metadata

if TYPE_CHECKING:
    from sila2_interop_communication_tester.test_server.server_implementation.server import ServerState


def validate_RequiresTokenForBinaryUpload_parameter_upload(
    metadata_dict: MetadataDict, context: grpc.ServicerContext, server_state: ServerState
):
    token_metadata = metadata_dict.get(AuthorizationService_pb2.Metadata_AccessToken)
    if token_metadata is None:
        raise_invalid_metadata_error(
            context, "Missing metadata: 'org.silastandard/core/AuthorizationService/v1/Metadata/AccessToken'"
        )

    token = token_metadata.AccessToken.value
    if token not in server_state.auth_tokens:
        raise_defined_execution_error(
            context,
            "org.silastandard/core/AuthorizationService/v1/DefinedExecutionError/InvalidAccessToken",
            "Invalid access token",
        )


class AuthenticationTestImpl(AuthenticationTestServicer):
    def __init__(self, server_state: ServerState) -> None:
        self.server_state = server_state

    def RequiresToken(
        self, request: AuthenticationTest_pb2.RequiresToken_Parameters, context: grpc.ServicerContext
    ) -> AuthenticationTest_pb2.RequiresToken_Responses:
        metadata = extract_metadata(context)
        if Metadata_AccessToken not in metadata:
            raise_invalid_metadata_error(context, "Missing metadata 'Access Token'")
        token = metadata[Metadata_AccessToken].AccessToken.value
        if token not in self.server_state.auth_tokens or self.server_state.auth_tokens[token] < datetime.now():
            raise_defined_execution_error(
                context,
                "org.silastandard/core/AuthorizationService/v1/DefinedExecutionError/InvalidAccessToken",
                "Invalid access token",
            )
        return AuthenticationTest_pb2.RequiresToken_Responses()

    def RequiresTokenForBinaryUpload(
        self, request: AuthenticationTest_pb2.RequiresTokenForBinaryUpload_Parameters, context: grpc.ServicerContext
    ) -> AuthenticationTest_pb2.RequiresTokenForBinaryUpload_Responses:
        # check metadata
        metadata = extract_metadata(context)
        if Metadata_AccessToken not in metadata:
            raise_invalid_metadata_error(context, "Missing metadata 'Access Token'")
        token = metadata[Metadata_AccessToken].AccessToken.value
        if token not in self.server_state.auth_tokens or self.server_state.auth_tokens[token] < datetime.now():
            raise_defined_execution_error(
                context,
                "org.silastandard/core/AuthorizationService/v1/DefinedExecutionError/InvalidAccessToken",
                "Invalid access token",
            )

        if not request.HasField("BinaryToUpload"):
            raise_validation_error(
                context,
                (
                    "org.silastandard/test/AuthenticationTest/v1/Command/RequiresTokenForBinaryUpload/"
                    "Parameter/BinaryToUpload"
                ),
                "Missing parameter 'Binary To Upload",
            )

        get_binary(
            request.BinaryToUpload,
            "org.silastandard/test/AuthenticationTest/v1/Command/RequiresTokenForBinaryUpload/Parameter/BinaryToUpload",
            context,
        )
        return AuthenticationTest_pb2.RequiresToken_Responses()
