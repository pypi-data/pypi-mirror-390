from sila2_interop_communication_tester.grpc_stubs import SiLAService_pb2
from sila2_interop_communication_tester.grpc_stubs.SiLAService_pb2_grpc import SiLAServiceStub


def get_server_uuid(silaservice_stub: SiLAServiceStub) -> str:
    return silaservice_stub.Get_ServerUUID(SiLAService_pb2.Get_ServerUUID_Parameters()).ServerUUID.value
