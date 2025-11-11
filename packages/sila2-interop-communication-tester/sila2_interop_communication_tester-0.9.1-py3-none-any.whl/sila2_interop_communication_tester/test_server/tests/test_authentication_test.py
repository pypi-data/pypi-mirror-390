from pytest import fail

from sila2_interop_communication_tester.helpers.utils import string_is_uuid
from sila2_interop_communication_tester.test_server.tests.test_binary_transfer import get_uploaded_binary


def test_command_without_parameters_called(server_calls):
    """
    Assert that the command AuthenticationTest.RequiresToken was called with a valid auth token
    """
    calls = server_calls["AuthenticationTest.RequiresToken"]
    assert any(
        call.successful for call in calls
    ), "AuthenticationTest.RequiresToken was never called with a valid auth token obtained via Login"


def test_command_called_with_small_binary(server_calls):
    """
    Assert that AuthenticationTest.RequiresTokenForBinaryUpload was called with a valid auth token
    and the ASCII-encoded byte string 'abc'
    """
    calls = server_calls["AuthenticationTest.RequiresTokenForBinaryUpload"]
    for call in calls:
        if not call.successful:
            continue
        if not call.request.HasField("BinaryToUpload"):
            continue
        if call.request.BinaryToUpload.value == b"abc":
            return
    fail(
        "AuthenticationTest.RequiresToken was never called with a valid auth token obtained "
        "via Login and 'abc' as parameter"
    )


def test_command_called_with_large_binary(server_calls):
    """
    Assert that a large binary with the ASCII-encoded string 'abc' repeated 1,000,000 times was uploaded for the command
    AuthenticationTest.RequiresTokenForBinaryUpload with a valid auth token, and that this command was then called with
    a valid auth token and the binary transfer UUID of the previously uploaded binary
    """
    calls = server_calls["AuthenticationTest.RequiresTokenForBinaryUpload"]
    for call in calls:
        if not call.successful:
            continue
        if not call.request.HasField("BinaryToUpload"):
            continue
        if string_is_uuid(call.request.BinaryToUpload.binaryTransferUUID) and (
            get_uploaded_binary(
                server_calls,
                call.request.BinaryToUpload.binaryTransferUUID,
                "org.silastandard/test/AuthenticationTest/v1/Command/RequiresTokenForBinaryUpload/Parameter/BinaryToUpload",
            )
            == b"abc" * 1_000_000
        ):
            return
    fail(
        "AuthenticationTest.RequiresToken was never called with a valid auth token obtained "
        "via Login and 'abc' repeated 1,000,000 times as parameter"
    )
