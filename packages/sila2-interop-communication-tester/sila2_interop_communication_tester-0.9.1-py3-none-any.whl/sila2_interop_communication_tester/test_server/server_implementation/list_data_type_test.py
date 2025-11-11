import grpc

from sila2_interop_communication_tester.grpc_stubs.ListDataTypeTest_pb2 import (
    DataType_TestStructure,
    EchoIntegerList_Parameters,
    EchoIntegerList_Responses,
    EchoStringList_Parameters,
    EchoStringList_Responses,
    EchoStructureList_Parameters,
    EchoStructureList_Responses,
    Get_EmptyStringList_Parameters,
    Get_EmptyStringList_Responses,
    Get_IntegerList_Parameters,
    Get_IntegerList_Responses,
    Get_StringList_Parameters,
    Get_StringList_Responses,
    Get_StructureList_Parameters,
    Get_StructureList_Responses,
)
from sila2_interop_communication_tester.grpc_stubs.ListDataTypeTest_pb2_grpc import (
    ListDataTypeTestServicer,
)
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import (
    Any,
    Binary,
    Boolean,
    Date,
    Integer,
    Real,
    String,
    Time,
    Timestamp,
    Timezone,
)
from sila2_interop_communication_tester.helpers.protobuf_helpers import (
    create_any_message,
)
from sila2_interop_communication_tester.test_server.helpers.raise_error import (
    raise_validation_error,
)


class ListDataTypeTestImpl(ListDataTypeTestServicer):
    def EchoStringList(
        self,
        request: EchoStringList_Parameters,
        context: grpc.ServicerContext,
    ) -> EchoStringList_Responses:
        for StringValue in request.StringList:
            if len(StringValue.value) > 2**21:
                raise_validation_error(
                    context,
                    "org.silastandard/test/ListDataTypeTest/v1/Command/EchoStringList/Parameter/StringList",
                    "String must not exceed 2²¹ characters",
                )

        return EchoStringList_Responses(ReceivedValues=request.StringList)

    def EchoIntegerList(
        self,
        request: EchoIntegerList_Parameters,
        context: grpc.ServicerContext,
    ) -> EchoIntegerList_Responses:
        return EchoIntegerList_Responses(ReceivedValues=request.IntegerList)

    def EchoStructureList(
        self,
        request: EchoStructureList_Parameters,
        context: grpc.ServicerContext,
    ) -> EchoStructureList_Responses:
        return EchoStructureList_Responses(ReceivedValues=request.StructureList)

    def Get_EmptyStringList(
        self,
        request: Get_EmptyStringList_Parameters,
        context: grpc.ServicerContext,
    ) -> Get_EmptyStringList_Responses:
        return Get_EmptyStringList_Responses(EmptyStringList=[])

    def Get_StringList(
        self,
        request: Get_StringList_Parameters,
        context: grpc.ServicerContext,
    ) -> Get_StringList_Responses:
        return Get_StringList_Responses(
            StringList=[
                String(value="SiLA 2"),
                String(value="is"),
                String(value="great"),
            ]
        )

    def Get_IntegerList(
        self,
        request: Get_IntegerList_Parameters,
        context: grpc.ServicerContext,
    ) -> Get_IntegerList_Responses:
        return Get_IntegerList_Responses(
            IntegerList=[
                Integer(value=1),
                Integer(value=2),
                Integer(value=3),
            ]
        )

    def Get_StructureList(
        self,
        request: Get_StructureList_Parameters,
        context: grpc.ServicerContext,
    ) -> Get_StructureList_Responses:
        return Get_StructureList_Responses(
            StructureList=[
                DataType_TestStructure(
                    TestStructure=DataType_TestStructure.TestStructure_Struct(
                        StringTypeValue=String(value="SiLA2_Test_String_Value_1"),
                        IntegerTypeValue=Integer(value=5124),
                        RealTypeValue=Real(value=3.1415926),
                        BooleanTypeValue=Boolean(value=True),
                        BinaryTypeValue=Binary(value=b"Binary_String_Value_1"),
                        DateTypeValue=Date(
                            year=2022,
                            month=8,
                            day=5,
                            timezone=Timezone(hours=2, minutes=0),
                        ),
                        TimeTypeValue=Time(
                            hour=12,
                            minute=34,
                            second=56,
                            timezone=Timezone(hours=2, minutes=0),
                        ),
                        TimestampTypeValue=Timestamp(
                            year=2022,
                            month=8,
                            day=5,
                            hour=12,
                            minute=34,
                            second=56,
                            timezone=Timezone(hours=2, minutes=0),
                        ),
                        AnyTypeValue=create_any_message(
                            type_xml="<DataType><Basic>String</Basic></DataType>",
                            value=String(value="Any_Type_String_Value_1"),
                        ),
                    ),
                ),
                DataType_TestStructure(
                    TestStructure=DataType_TestStructure.TestStructure_Struct(
                        StringTypeValue=String(value="SiLA2_Test_String_Value_2"),
                        IntegerTypeValue=Integer(value=5125),
                        RealTypeValue=Real(value=4.1415926),
                        BooleanTypeValue=Boolean(value=False),
                        BinaryTypeValue=Binary(value=b"Binary_String_Value_2"),
                        DateTypeValue=Date(
                            year=2023,
                            month=9,
                            day=6,
                            timezone=Timezone(hours=2, minutes=0),
                        ),
                        TimeTypeValue=Time(
                            hour=13,
                            minute=35,
                            second=57,
                            timezone=Timezone(hours=2, minutes=0),
                        ),
                        TimestampTypeValue=Timestamp(
                            year=2023,
                            month=9,
                            day=6,
                            hour=13,
                            minute=35,
                            second=57,
                            timezone=Timezone(hours=2, minutes=0),
                        ),
                        AnyTypeValue=create_any_message(
                            type_xml="<DataType><Basic>String</Basic></DataType>",
                            value=String(value="Any_Type_String_Value_2"),
                        ),
                    ),
                ),
                DataType_TestStructure(
                    TestStructure=DataType_TestStructure.TestStructure_Struct(
                        StringTypeValue=String(value="SiLA2_Test_String_Value_3"),
                        IntegerTypeValue=Integer(value=5126),
                        RealTypeValue=Real(value=5.1415926),
                        BooleanTypeValue=Boolean(value=True),
                        BinaryTypeValue=Binary(value=b"Binary_String_Value_3"),
                        DateTypeValue=Date(
                            year=2024,
                            month=10,
                            day=7,
                            timezone=Timezone(hours=2, minutes=0),
                        ),
                        TimeTypeValue=Time(
                            hour=14,
                            minute=36,
                            second=58,
                            millisecond=789,
                            timezone=Timezone(hours=2, minutes=0),
                        ),
                        TimestampTypeValue=Timestamp(
                            year=2024,
                            month=10,
                            day=7,
                            hour=14,
                            minute=36,
                            second=58,
                            millisecond=789,
                            timezone=Timezone(hours=2, minutes=0),
                        ),
                        AnyTypeValue=create_any_message(
                            type_xml="<DataType><Basic>String</Basic></DataType>",
                            value=String(value="Any_Type_String_Value_3"),
                        ),
                    ),
                ),
            ]
        )
