from sila2_interop_communication_tester.grpc_stubs import AuthorizationService_pb2


def test_accesstoken_affects_authenticationtest_feature(authorizationservice_stub):
    """The AccessToken metadata must affect either the full AuthenticationService feature, or both of its commands."""
    raw_affected_calls = authorizationservice_stub.Get_FCPAffectedByMetadata_AccessToken(
        AuthorizationService_pb2.Get_FCPAffectedByMetadata_AccessToken_Parameters()
    )
    affected_calls = {call.value for call in raw_affected_calls.AffectedCalls}

    assert "org.silastandard/test/AuthenticationTest/v1" in affected_calls or (
        "org.silastandard/test/AuthenticationTest/v1/Command/RequiresToken" in affected_calls
        and "org.silastandard/test/AuthenticationTest/v1/Command/RequiresTokenForBinaryUpload" in affected_calls
    )
