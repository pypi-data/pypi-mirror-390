import grpc

from sila2_interop_communication_tester.grpc_stubs.BasicDataTypesTest_pb2 import (
    EchoBooleanValue_Parameters,
    EchoBooleanValue_Responses,
    EchoDateValue_Parameters,
    EchoDateValue_Responses,
    EchoIntegerValue_Parameters,
    EchoIntegerValue_Responses,
    EchoRealValue_Parameters,
    EchoRealValue_Responses,
    EchoStringValue_Parameters,
    EchoStringValue_Responses,
    EchoTimestampValue_Parameters,
    EchoTimestampValue_Responses,
    EchoTimeValue_Parameters,
    EchoTimeValue_Responses,
    Get_BooleanValue_Parameters,
    Get_BooleanValue_Responses,
    Get_DateValue_Parameters,
    Get_DateValue_Responses,
    Get_IntegerValue_Parameters,
    Get_IntegerValue_Responses,
    Get_RealValue_Parameters,
    Get_RealValue_Responses,
    Get_StringValue_Parameters,
    Get_StringValue_Responses,
    Get_TimestampValue_Parameters,
    Get_TimestampValue_Responses,
    Get_TimeValue_Parameters,
    Get_TimeValue_Responses,
)
from sila2_interop_communication_tester.grpc_stubs.BasicDataTypesTest_pb2_grpc import (
    BasicDataTypesTestServicer,
)
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import (
    Boolean,
    Date,
    Integer,
    Real,
    String,
    Time,
    Timestamp,
    Timezone,
)
from sila2_interop_communication_tester.test_server.helpers.raise_error import (
    raise_validation_error,
)


class BasicDataTypesTestImpl(BasicDataTypesTestServicer):
    def EchoStringValue(
        self,
        request: EchoStringValue_Parameters,
        context: grpc.ServicerContext,
    ) -> EchoStringValue_Responses:
        if not request.HasField("StringValue"):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoStringValue/Parameter/StringValue",
                "Missing parameter",
            )

        if len(request.StringValue.value) > 2**21:
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoStringValue/Parameter/StringValue",
                "String must not exceed 2²¹ characters",
            )

        return EchoStringValue_Responses(ReceivedValue=request.StringValue)

    def EchoIntegerValue(
        self,
        request: EchoIntegerValue_Parameters,
        context: grpc.ServicerContext,
    ) -> EchoIntegerValue_Responses:
        if not request.HasField("IntegerValue"):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoIntegerValue/Parameter/IntegerValue",
                "Missing parameter",
            )

        return EchoIntegerValue_Responses(ReceivedValue=request.IntegerValue)

    def EchoRealValue(
        self,
        request: EchoRealValue_Parameters,
        context: grpc.ServicerContext,
    ) -> EchoRealValue_Responses:
        if not request.HasField("RealValue"):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoRealValue/Parameter/RealValue",
                "Missing parameter",
            )

        return EchoRealValue_Responses(ReceivedValue=request.RealValue)

    def EchoBooleanValue(
        self,
        request: EchoBooleanValue_Parameters,
        context: grpc.ServicerContext,
    ) -> EchoBooleanValue_Responses:
        if not request.HasField("BooleanValue"):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoBooleanValue/Parameter/BooleanValue",
                "Missing parameter",
            )

        return EchoBooleanValue_Responses(ReceivedValue=request.BooleanValue)

    def EchoDateValue(
        self,
        request: EchoDateValue_Parameters,
        context: grpc.ServicerContext,
    ) -> EchoDateValue_Responses:
        if not request.HasField("DateValue"):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue",
                "Missing parameter",
            )
        if not request.DateValue.HasField("timezone"):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue",
                "Missing timezone",
            )

        if not (1 <= request.DateValue.year <= 9999):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue",
                "Year must be between 1 and 9999",
            )

        if not (1 <= request.DateValue.month <= 12):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue",
                "Month must be between 1 and 12",
            )

        if not (1 <= request.DateValue.day <= 31):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue",
                "Day must be between 1 and 31",
            )

        if not (-840 <= (request.DateValue.timezone.hours * 60 + request.DateValue.timezone.minutes) <= 840):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue",
                "Timezone must be between -14:00 and +14:00",
            )

        if not (0 <= request.DateValue.timezone.minutes <= 59):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoDateValue/Parameter/DateValue",
                "Timezone minutes must be between 0 and 59",
            )

        return EchoDateValue_Responses(ReceivedValue=request.DateValue)

    def EchoTimeValue(
        self,
        request: EchoTimeValue_Parameters,
        context: grpc.ServicerContext,
    ) -> EchoTimeValue_Responses:
        if not request.HasField("TimeValue"):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue",
                "Missing parameter",
            )
        if not request.TimeValue.HasField("timezone"):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue",
                "Missing timezone",
            )

        if not (0 <= request.TimeValue.hour <= 23):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue",
                "Hour must be between 0 and 23",
            )

        if not (0 <= request.TimeValue.minute <= 59):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue",
                "Minute must be between 0 and 59",
            )

        if not (0 <= request.TimeValue.second <= 59):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue",
                "Second must be between 0 and 59",
            )

        if not (0 <= request.TimeValue.millisecond <= 999):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue",
                "Millisecond must be between 0 and 999",
            )

        if not (-840 <= (request.TimeValue.timezone.hours * 60 + request.TimeValue.timezone.minutes) <= 840):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue",
                "Timezone must be between -14:00 and +14:00",
            )

        if not (0 <= request.TimeValue.timezone.minutes <= 59):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimeValue/Parameter/TimeValue",
                "Timezone minutes must be between 0 and 59",
            )

        return EchoTimeValue_Responses(ReceivedValue=request.TimeValue)

    def EchoTimestampValue(
        self,
        request: EchoTimestampValue_Parameters,
        context: grpc.ServicerContext,
    ) -> EchoTimestampValue_Responses:
        if not request.HasField("TimestampValue"):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue",
                "Missing parameter",
            )
        if not request.TimestampValue.HasField("timezone"):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue",
                "Missing timezone",
            )

        if not (1 <= request.TimestampValue.year <= 9999):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue",
                "Year must be between 1 and 9999",
            )

        if not (1 <= request.TimestampValue.month <= 12):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue",
                "Month must be between 1 and 12",
            )

        if not (1 <= request.TimestampValue.day <= 31):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue",
                "Day must be between 1 and 31",
            )

        if not (0 <= request.TimestampValue.hour <= 23):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue",
                "Hour must be between 0 and 23",
            )

        if not (0 <= request.TimestampValue.minute <= 59):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue",
                "Minute must be between 0 and 59",
            )

        if not (0 <= request.TimestampValue.second <= 59):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue",
                "Second must be between 0 and 59",
            )

        if not (0 <= request.TimestampValue.millisecond <= 999):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue",
                "Millisecond must be between 0 and 999",
            )

        if not (-840 <= (request.TimestampValue.timezone.hours * 60 + request.TimestampValue.timezone.minutes) <= 840):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue",
                "Timezone must be between -14:00 and +14:00",
            )

        if not (0 <= request.TimestampValue.timezone.minutes <= 59):
            raise_validation_error(
                context,
                "org.silastandard/test/BasicDataTypesTest/v1/Command/EchoTimestampValue/Parameter/TimestampValue",
                "Timezone minutes must be between 0 and 59",
            )

        return EchoTimestampValue_Responses(ReceivedValue=request.TimestampValue)

    def Get_StringValue(
        self,
        request: Get_StringValue_Parameters,
        context: grpc.ServicerContext,
    ) -> Get_StringValue_Responses:
        return Get_StringValue_Responses(
            StringValue=String(value="SiLA2_Test_String_Value")
        )

    def Get_IntegerValue(
        self,
        request: Get_IntegerValue_Parameters,
        context: grpc.ServicerContext,
    ) -> Get_IntegerValue_Responses:
        return Get_IntegerValue_Responses(IntegerValue=Integer(value=5124))

    def Get_RealValue(
        self,
        request: Get_RealValue_Parameters,
        context: grpc.ServicerContext,
    ) -> Get_RealValue_Responses:
        return Get_RealValue_Responses(RealValue=Real(value=3.1415926))

    def Get_BooleanValue(
        self,
        request: Get_BooleanValue_Parameters,
        context: grpc.ServicerContext,
    ) -> Get_BooleanValue_Responses:
        return Get_BooleanValue_Responses(BooleanValue=Boolean(value=True))

    def Get_DateValue(
        self,
        request: Get_DateValue_Parameters,
        context: grpc.ServicerContext,
    ) -> Get_DateValue_Responses:
        return Get_DateValue_Responses(
            DateValue=Date(year=2022, month=8, day=5, timezone=Timezone(hours=2))
        )

    def Get_TimeValue(
        self,
        request: Get_TimeValue_Parameters,
        context: grpc.ServicerContext,
    ) -> Get_TimeValue_Responses:
        return Get_TimeValue_Responses(
            TimeValue=Time(
                hour=12,
                minute=34,
                second=56,
                millisecond=789,
                timezone=Timezone(hours=2),
            )
        )

    def Get_TimestampValue(
        self,
        request: Get_TimestampValue_Parameters,
        context: grpc.ServicerContext,
    ) -> Get_TimestampValue_Responses:
        return Get_TimestampValue_Responses(
            TimestampValue=Timestamp(
                year=2022,
                month=8,
                day=5,
                hour=12,
                minute=34,
                second=56,
                millisecond=789,
                timezone=Timezone(hours=2),
            )
        )
