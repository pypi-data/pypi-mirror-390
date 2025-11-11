import grpc

from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import (
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
from sila2_interop_communication_tester.grpc_stubs.StructureDataTypeTest_pb2 import (
    DataType_DeepStructure,
    DataType_TestStructure,
    EchoDeepStructureValue_Parameters,
    EchoDeepStructureValue_Responses,
    EchoStructureValue_Parameters,
    EchoStructureValue_Responses,
    Get_DeepStructureValue_Parameters,
    Get_DeepStructureValue_Responses,
    Get_StructureValue_Parameters,
    Get_StructureValue_Responses,
)
from sila2_interop_communication_tester.grpc_stubs.StructureDataTypeTest_pb2_grpc import (
    StructureDataTypeTestServicer,
)
from sila2_interop_communication_tester.helpers.protobuf_helpers import create_any_message
from sila2_interop_communication_tester.test_server.helpers.raise_error import (
    raise_validation_error,
)


class StructureDataTypeTestImpl(StructureDataTypeTestServicer):
    def EchoStructureValue(
        self,
        request: EchoStructureValue_Parameters,
        context: grpc.ServicerContext,
    ) -> EchoStructureValue_Responses:
        if not request.HasField("StructureValue"):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Missing parameter",
            )

        if len(request.StructureValue.TestStructure.StringTypeValue.value) > 2**21:
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "String must not exceed 2²¹ characters",
            )

        if not (1 <= request.StructureValue.TestStructure.DateTypeValue.year <= 9999):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Year must be between 1 and 9999",
            )

        if not (
            1 <= request.StructureValue.TestStructure.TimestampTypeValue.year <= 9999
        ):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Year must be between 1 and 9999",
            )

        if not (1 <= request.StructureValue.TestStructure.DateTypeValue.month <= 12):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Month must be between 1 and 12",
            )
        if not (
            1 <= request.StructureValue.TestStructure.TimestampTypeValue.month <= 12
        ):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Month must be between 1 and 12",
            )

        if not (1 <= request.StructureValue.TestStructure.DateTypeValue.day <= 31):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Day must be between 1 and 31",
            )

        if not (1 <= request.StructureValue.TestStructure.TimestampTypeValue.day <= 31):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Day must be between 1 and 31",
            )

        if not (0 <= request.StructureValue.TestStructure.TimeTypeValue.hour <= 23):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Hour must be between 0 and 23",
            )

        if not (
            0 <= request.StructureValue.TestStructure.TimestampTypeValue.hour <= 23
        ):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Hour must be between 0 and 23",
            )

        if not (0 <= request.StructureValue.TestStructure.TimeTypeValue.minute <= 59):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Minute must be between 0 and 59",
            )

        if not (
            0 <= request.StructureValue.TestStructure.TimestampTypeValue.minute <= 59
        ):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Minute must be between 0 and 59",
            )

        if not (0 <= request.StructureValue.TestStructure.TimeTypeValue.second <= 59):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Second must be between 0 and 59",
            )

        if not (
            0 <= request.StructureValue.TestStructure.TimestampTypeValue.second <= 59
        ):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Second must be between 0 and 59",
            )

        if not (
            0 <= request.StructureValue.TestStructure.TimeTypeValue.millisecond <= 999
        ):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Millisecond must be between 0 and 999",
            )

        if not (
            0
            <= request.StructureValue.TestStructure.TimestampTypeValue.millisecond
            <= 999
        ):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Millisecond must be between 0 and 999",
            )

        if not (
            -12
            <= request.StructureValue.TestStructure.DateTypeValue.timezone.hours
            <= 14
        ):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Hours must be between -12 and 14",
            )

        if not (
            -12
            <= request.StructureValue.TestStructure.TimeTypeValue.timezone.hours
            <= 14
        ):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Hours must be between -12 and 14",
            )

        if not (
            -12
            <= request.StructureValue.TestStructure.TimestampTypeValue.timezone.hours
            <= 14
        ):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Hours must be between -12 and 14",
            )

        if not (
            0
            <= request.StructureValue.TestStructure.DateTypeValue.timezone.minutes
            <= 59
        ):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Minutes must be between 0 and 59",
            )

        if not (
            0
            <= request.StructureValue.TestStructure.TimeTypeValue.timezone.minutes
            <= 59
        ):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Minutes must be between 0 and 59",
            )

        if not (
            0
            <= request.StructureValue.TestStructure.TimestampTypeValue.timezone.minutes
            <= 59
        ):
            raise_validation_error(
                context,
                "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoStructureValue/Parameter/StructureValue",
                "Minutes must be between 0 and 59",
            )

        return EchoStructureValue_Responses(ReceivedValues=request.StructureValue)

    def EchoDeepStructureValue(
        self,
        request: EchoDeepStructureValue_Parameters,
        context: grpc.ServicerContext,
    ) -> EchoDeepStructureValue_Responses:
        parameter_id = "org.silastandard/test/StructureDataTypeTest/v1/Command/EchoDeepStructureValue/Parameter/DeepStructureValue"
        if not request.HasField("DeepStructureValue"):
            raise_validation_error(context, parameter_id, "Missing parameter")
        if not request.DeepStructureValue.HasField("DeepStructure"):
            raise_validation_error(context, parameter_id, "Missing structure field DeepStructureValue.DeepStructure")
        if not request.DeepStructureValue.DeepStructure.HasField("OuterStringTypeValue"):
            raise_validation_error(context, parameter_id, "Missing structure field DeepStructureValue.DeepStructure.OuterStringTypeValue")
        if not request.DeepStructureValue.DeepStructure.HasField("OuterIntegerTypeValue"):
            raise_validation_error(context, parameter_id, "Missing structure field DeepStructureValue.DeepStructure.OuterIntegerTypeValue")
        if not request.DeepStructureValue.DeepStructure.HasField("MiddleStructure"):
            raise_validation_error(context, parameter_id, "Missing structure field DeepStructureValue.DeepStructure.MiddleStructure")
        if not request.DeepStructureValue.DeepStructure.MiddleStructure.HasField("MiddleStringTypeValue"):
            raise_validation_error(context, parameter_id, "Missing structure field DeepStructureValue.DeepStructure.MiddleStructure.MiddleStringTypeValue")
        if not request.DeepStructureValue.DeepStructure.MiddleStructure.HasField("MiddleIntegerTypeValue"):
            raise_validation_error(context, parameter_id, "Missing structure field DeepStructureValue.DeepStructure.MiddleStructure.MiddleIntegerTypeValue")
        if not request.DeepStructureValue.DeepStructure.MiddleStructure.HasField("InnerStructure"):
            raise_validation_error(context, parameter_id, "Missing structure field DeepStructureValue.DeepStructure.MiddleStructure.InnerStructure")
        if not request.DeepStructureValue.DeepStructure.MiddleStructure.InnerStructure.HasField("InnerStringTypeValue"):
            raise_validation_error(context, parameter_id, "Missing structure field DeepStructureValue.DeepStructure.MiddleStructure.InnerStructure.InnerStringTypeValue")
        if not request.DeepStructureValue.DeepStructure.MiddleStructure.InnerStructure.HasField("InnerIntegerTypeValue"):
            raise_validation_error(context, parameter_id, "Missing structure field DeepStructureValue.DeepStructure.MiddleStructure.InnerStructure.InnerIntegerTypeValue")

        outer_string = request.DeepStructureValue.DeepStructure.OuterStringTypeValue.value
        if len(outer_string) > 2**21:
            raise_validation_error(context, parameter_id, "String must not exceed 2²¹ characters (element DeepStructureValue.DeepStructure.OuterStringTypeValue)")
        middle_string = request.DeepStructureValue.DeepStructure.MiddleStructure.MiddleStringTypeValue.value
        if len(middle_string) > 2**21:
            raise_validation_error(context, parameter_id, "String must not exceed 2²¹ characters (element DeepStructureValue.DeepStructure.MiddleStructure.MiddleStringTypeValue)")
        inner_string = request.DeepStructureValue.DeepStructure.MiddleStructure.InnerStructure.InnerStringTypeValue.value
        if len(inner_string) > 2**21:
            raise_validation_error(context, parameter_id, "String must not exceed 2²¹ characters (element DeepStructureValue.DeepStructure.MiddleStructure.InnerStructure.InnerStringTypeValue)")

        return EchoDeepStructureValue_Responses(
            ReceivedValues=request.DeepStructureValue
        )

    def Get_StructureValue(
        self,
        request: Get_StructureValue_Parameters,
        context: grpc.ServicerContext,
    ) -> Get_StructureValue_Responses:
        return Get_StructureValue_Responses(
            StructureValue=DataType_TestStructure(
                TestStructure=DataType_TestStructure.TestStructure_Struct(
                    StringTypeValue=String(value="SiLA2_Test_String_Value"),
                    IntegerTypeValue=Integer(value=5124),
                    RealTypeValue=Real(value=3.1415926),
                    BooleanTypeValue=Boolean(value=True),
                    BinaryTypeValue=Binary(value=b"SiLA2_Binary_String_Value"),
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
                        millisecond=789,
                        timezone=Timezone(hours=2, minutes=0),
                    ),
                    TimestampTypeValue=Timestamp(
                        year=2022,
                        month=8,
                        day=5,
                        hour=12,
                        minute=34,
                        second=56,
                        millisecond=789,
                        timezone=Timezone(hours=2, minutes=0),
                    ),
                    AnyTypeValue=create_any_message(
                        type_xml="<DataType><Basic>String</Basic></DataType>",
                        value=String(value="SiLA2_Any_Type_String_Value"),
                    ),
                ),
            )
        )

    def Get_DeepStructureValue(
        self,
        request: Get_DeepStructureValue_Parameters,
        context: grpc.ServicerContext,
    ) -> Get_DeepStructureValue_Responses:
        return Get_DeepStructureValue_Responses(
            DeepStructureValue=DataType_DeepStructure(
                DeepStructure=DataType_DeepStructure.DeepStructure_Struct(
                    OuterStringTypeValue=String(value="Outer_Test_String"),
                    OuterIntegerTypeValue=Integer(value=1111),
                    MiddleStructure=DataType_DeepStructure.DeepStructure_Struct.MiddleStructure_Struct(
                        MiddleStringTypeValue=String(value="Middle_Test_String"),
                        MiddleIntegerTypeValue=Integer(value=2222),
                        InnerStructure=DataType_DeepStructure.DeepStructure_Struct.MiddleStructure_Struct.InnerStructure_Struct(
                            InnerStringTypeValue=String(value="Inner_Test_String"),
                            InnerIntegerTypeValue=Integer(value=3333),
                        ),
                    ),
                )
            ),
        )
