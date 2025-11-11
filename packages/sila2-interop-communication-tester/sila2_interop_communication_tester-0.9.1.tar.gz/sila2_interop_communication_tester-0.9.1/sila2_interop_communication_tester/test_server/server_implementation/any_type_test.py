import grpc

from sila2_interop_communication_tester.grpc_stubs.AnyTypeTest_pb2 import (
    Get_AnyTypeBinaryValue_Parameters,
    Get_AnyTypeBinaryValue_Responses,
    Get_AnyTypeBooleanValue_Parameters,
    Get_AnyTypeBooleanValue_Responses,
    Get_AnyTypeDateValue_Parameters,
    Get_AnyTypeDateValue_Responses,
    Get_AnyTypeIntegerValue_Parameters,
    Get_AnyTypeIntegerValue_Responses,
    Get_AnyTypeListValue_Parameters,
    Get_AnyTypeListValue_Responses,
    Get_AnyTypeRealValue_Parameters,
    Get_AnyTypeRealValue_Responses,
    Get_AnyTypeStringValue_Parameters,
    Get_AnyTypeStringValue_Responses,
    Get_AnyTypeStructureValue_Parameters,
    Get_AnyTypeStructureValue_Responses,
    Get_AnyTypeTimestampValue_Parameters,
    Get_AnyTypeTimestampValue_Responses,
    Get_AnyTypeTimeValue_Parameters,
    Get_AnyTypeTimeValue_Responses,
    SetAnyTypeValue_Parameters,
    SetAnyTypeValue_Responses,
)
from sila2_interop_communication_tester.grpc_stubs.AnyTypeTest_pb2_grpc import (
    AnyTypeTestServicer,
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
from sila2_interop_communication_tester.helpers.protobuf_helpers import create_any_message


class AnyTypeTestImpl(AnyTypeTestServicer):
    def SetAnyTypeValue(
        self, request: SetAnyTypeValue_Parameters, context: grpc.ServicerContext
    ):
        return SetAnyTypeValue_Responses(
            ReceivedAnyType=String(value=request.AnyTypeValue.type),
            ReceivedValue=request.AnyTypeValue,
        )

    def Get_AnyTypeStringValue(
        self, request: Get_AnyTypeStringValue_Parameters, context: grpc.ServicerContext
    ):
        return Get_AnyTypeStringValue_Responses(
            AnyTypeStringValue=create_any_message(
                type_xml="<DataType><Basic>String</Basic></DataType>",
                value=String(
                    value="SiLA_Any_type_of_String_type"
                ),
            )
        )

    def Get_AnyTypeIntegerValue(
        self, request: Get_AnyTypeIntegerValue_Parameters, context: grpc.ServicerContext
    ):
        return Get_AnyTypeIntegerValue_Responses(
            AnyTypeIntegerValue=create_any_message(
                type_xml="<DataType><Basic>Integer</Basic></DataType>",
                value=Integer(value=5124),
            )
        )

    def Get_AnyTypeRealValue(
        self, request: Get_AnyTypeRealValue_Parameters, context: grpc.ServicerContext
    ):
        return Get_AnyTypeRealValue_Responses(
            AnyTypeRealValue=create_any_message(
                type_xml="<DataType><Basic>Real</Basic></DataType>",
                value=Real(value=3.1415926),
            )
        )

    def Get_AnyTypeBooleanValue(
        self, request: Get_AnyTypeBooleanValue_Parameters, context: grpc.ServicerContext
    ):
        return Get_AnyTypeBooleanValue_Responses(
            AnyTypeBooleanValue=create_any_message(
                type_xml="<DataType><Basic>Boolean</Basic></DataType>",
                value=Boolean(value=True),
            )
        )

    def Get_AnyTypeBinaryValue(
        self, request: Get_AnyTypeBinaryValue_Parameters, context: grpc.ServicerContext
    ):
        return Get_AnyTypeBinaryValue_Responses(
            AnyTypeBinaryValue=create_any_message(
                type_xml="<DataType><Basic>Binary</Basic></DataType>",
                value=Binary(
                    value=b"SiLA_Any_type_of_Binary_type"
                ),
            )
        )

    def Get_AnyTypeDateValue(
        self, request: Get_AnyTypeDateValue_Parameters, context: grpc.ServicerContext
    ):
        return Get_AnyTypeDateValue_Responses(
            AnyTypeDateValue=create_any_message(
                type_xml="<DataType><Basic>Date</Basic></DataType>",
                value=Date(
                    year=2022, month=8, day=5, timezone=Timezone(hours=2)
                ),
            )
        )

    def Get_AnyTypeTimeValue(
        self, request: Get_AnyTypeTimeValue_Parameters, context: grpc.ServicerContext
    ):
        return Get_AnyTypeTimeValue_Responses(
            AnyTypeTimeValue=create_any_message(
                type_xml="<DataType><Basic>Time</Basic></DataType>",
                value=Time(
                    hour=12,
                    minute=34,
                    second=56,
                    millisecond=789,
                    timezone=Timezone(hours=2),
                ),
            )
        )

    def Get_AnyTypeTimestampValue(
        self,
        request: Get_AnyTypeTimestampValue_Parameters,
        context: grpc.ServicerContext,
    ):
        return Get_AnyTypeTimestampValue_Responses(
            AnyTypeTimestampValue=create_any_message(
                type_xml="<DataType><Basic>Timestamp</Basic></DataType>",
                value=Timestamp(
                    year=2022,
                    month=8,
                    day=5,
                    hour=12,
                    minute=34,
                    second=56,
                    millisecond=789,
                    timezone=Timezone(hours=2),
                ),
            )
        )

    def Get_AnyTypeListValue(
        self, request: Get_AnyTypeListValue_Parameters, context: grpc.ServicerContext
    ):
        return Get_AnyTypeListValue_Responses(
            AnyTypeListValue=create_any_message(
                type_xml="<DataType><List><DataType><Basic>String</Basic></DataType></List></DataType>",
                value=[
                    String(value="SiLA 2"),
                    String(value="Any"),
                    String(value="Type"),
                    String(value="String"),
                    String(value="List"),
                ],
            )
        )

    def Get_AnyTypeStructureValue(
        self,
        request: Get_AnyTypeStructureValue_Parameters,
        context: grpc.ServicerContext,
    ):
        return Get_AnyTypeStructureValue_Responses(
            AnyTypeStructureValue=Any(
                type="""
                    <DataType>
                        <Structure>
                            <Element>
                                <Identifier>StringTypeValue</Identifier>
                                <DisplayName>String Type Value</DisplayName>
                                <Description>A string value.</Description>
                                <DataType>
                                    <Basic>String</Basic>
                                </DataType>
                            </Element>
                            <Element>
                                <Identifier>IntegerTypeValue</Identifier>
                                <DisplayName>Integer Type Value</DisplayName>
                                <Description>An integer value.</Description>
                                <DataType>
                                    <Basic>Integer</Basic>
                                </DataType>
                            </Element>
                            <Element>
                                <Identifier>DateTypeValue</Identifier>
                                <DisplayName>Date Type Value</DisplayName>
                                <Description>A date value.</Description>
                                <DataType>
                                    <Basic>Date</Basic>
                                </DataType>
                            </Element>
                        </Structure>
                    </DataType>
                """.replace(" ", "").replace("\n", ""),
                payload=(
                    b"\x0a\x26"  # outer message: embedded message - 38 bytes (0x26)
                    + b"\x0a\x10"  # element 1: embedded message - 16 bytes (0x10)
                    + b"\x0a\x0e"  # value of element 1: String of length 14 (0x0e)
                    + b"A String value"
                    + b"\x12\x05"  # element 2: embedded message - 5 bytes (0x05)
                    + Integer(value=83737665).SerializeToString()
                    + b"\x1a\x0b"  # element 3: embedded message - 11 bytes(0x0b)
                    + Date(year=2022, month=8, day=5, timezone=Timezone(hours=2)).SerializeToString()
                ),
            )
        )
