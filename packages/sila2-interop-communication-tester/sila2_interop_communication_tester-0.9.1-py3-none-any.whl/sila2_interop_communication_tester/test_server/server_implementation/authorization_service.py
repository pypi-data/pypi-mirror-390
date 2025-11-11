import grpc

from sila2_interop_communication_tester.grpc_stubs import AuthorizationService_pb2, SiLAFramework_pb2
from sila2_interop_communication_tester.grpc_stubs.AuthorizationService_pb2_grpc import AuthorizationServiceServicer


class AuthorizationServiceImpl(AuthorizationServiceServicer):
    def Get_FCPAffectedByMetadata_AccessToken(
        self,
        request: AuthorizationService_pb2.Get_FCPAffectedByMetadata_AccessToken_Parameters,
        context: grpc.ServicerContext,
    ) -> AuthorizationService_pb2.Get_FCPAffectedByMetadata_AccessToken_Responses:
        return AuthorizationService_pb2.Get_FCPAffectedByMetadata_AccessToken_Responses(
            AffectedCalls=[SiLAFramework_pb2.String(value="org.silastandard/test/AuthenticationTest/v1")]
        )
