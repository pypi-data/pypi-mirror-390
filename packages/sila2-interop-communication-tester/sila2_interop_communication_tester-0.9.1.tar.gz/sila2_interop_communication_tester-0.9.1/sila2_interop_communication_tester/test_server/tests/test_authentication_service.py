def test_user_has_logged_out(server_calls):
    """
    Assert that AuthenticationService.Logout was called with a valid auth token
    """
    calls = server_calls["AuthenticationService.Logout"]
    assert any(call.successful for call in calls), "Logout was never called with a valid auth token obtained via Login"


def test_user_has_logged_in_with_test_test(server_calls):
    """
    Assert that the user has called AuthenticationService.Login with
    - the username 'test'
    - the password 'test'
    - the correct server UUID
    - the fully qualified feature identifier of the AuthorizationTest feature
    """
    calls = server_calls["AuthenticationService.Login"]
    assert any(call.successful for call in calls), (
        "Login was never called with username 'test', password 'test', the correct server UUID "
        "and the feature identifier of AuthorizationTest"
    )
