from sila2_interop_communication_tester.grpc_stubs import SiLAFramework_pb2
from sila2_interop_communication_tester.grpc_stubs.MetadataConsumerTest_pb2 import Get_ReceivedStringMetadata_Parameters
from sila2_interop_communication_tester.grpc_stubs.MetadataProvider_pb2 import Metadata_StringMetadata
from sila2_interop_communication_tester.test_client.helpers.error_handling import raises_invalid_metadata_error
from sila2_interop_communication_tester.test_client.helpers.utils import pack_metadata


def test_get_received_string_metadata_fails_without_metadata(metadataconsumertest_stub):
    with raises_invalid_metadata_error():
        metadataconsumertest_stub.Get_ReceivedStringMetadata(Get_ReceivedStringMetadata_Parameters())


def test_get_received_string_metadata_fails_with_empty_string_metadata(metadataconsumertest_stub):
    with raises_invalid_metadata_error():
        metadataconsumertest_stub.Get_ReceivedStringMetadata.with_call(
            request=Get_ReceivedStringMetadata_Parameters(), metadata=pack_metadata(Metadata_StringMetadata())
        )


def test_get_received_string_metadata_works_with_abc(metadataconsumertest_stub):
    response, _ = metadataconsumertest_stub.Get_ReceivedStringMetadata.with_call(
        request=Get_ReceivedStringMetadata_Parameters(),
        metadata=pack_metadata(Metadata_StringMetadata(StringMetadata=SiLAFramework_pb2.String(value="abc"))),
    )
    assert response.ReceivedStringMetadata.value == "abc"


def test_get_received_string_metadata_works_with_abcde(metadataconsumertest_stub):
    response, _ = metadataconsumertest_stub.Get_ReceivedStringMetadata.with_call(
        request=Get_ReceivedStringMetadata_Parameters(),
        metadata=pack_metadata(Metadata_StringMetadata(StringMetadata=SiLAFramework_pb2.String(value="abcde"))),
    )
    assert response.ReceivedStringMetadata.value == "abcde"
