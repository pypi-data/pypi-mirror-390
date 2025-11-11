import logging
import types
from base64 import b64decode
from collections import defaultdict
from collections.abc import Iterator
from datetime import datetime
from functools import wraps
from typing import Any, Mapping, NamedTuple, Optional, Type, TypeVar, Union

import grpc
from google.protobuf.message import Message
from grpc import ServicerContext

from sila2_interop_communication_tester.grpc_stubs.SiLABinaryTransfer_pb2 import BinaryTransferError
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import SiLAError
from sila2_interop_communication_tester.helpers.fdl_tools import fdl_xmls, xpath_sila
from sila2_interop_communication_tester.helpers.protobuf_helpers import get_message_class, message_to_string

logger = logging.getLogger(__name__)

T = TypeVar("T")  # subclass of Message. `bound=Message` would be correct, but is buggy in mypy


class MetadataDict(Mapping[Type[T], T]):
    def __init__(self, *messages: T) -> None:
        self.__dict: dict[Type[T], T] = {type(message): message for message in messages}

    def __getitem__(self, message_type: Type[T]) -> T:
        return self.__dict[message_type]

    def __len__(self) -> int:
        return len(self.__dict)

    def __iter__(self) -> Iterator[Type[T]]:
        return iter(self.__dict.keys())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({', '.join(message_to_string(message) for message in self.values())})"

    def __contains__(self, item: Any) -> bool:
        return item in self.__dict


class GrpcStatus(NamedTuple):
    code: grpc.StatusCode
    details: Union[str, bytes]
    streamed_responses: list[Message]

    def parse_error(self) -> Optional[Union[SiLAError, BinaryTransferError]]:
        details = self.details
        if isinstance(details, bytes) and self.code == grpc.StatusCode.ABORTED:
            try:
                serialized_message = b64decode(details)
                if serialized_message[0] == 0x08 or (
                    serialized_message[0] == 0x12 and serialized_message[-2:] == b"\x08\x01"
                ):
                    return BinaryTransferError.FromString(serialized_message)
                else:
                    return SiLAError.FromString(serialized_message)
            except BaseException:
                pass
        return None

    def __str__(self) -> str:
        error = self.parse_error()
        if error is None:
            return "".join(
                (
                    self.__class__.__name__,
                    "(",
                    f"code={self.code!r}, ",
                    f"details={self.details!r}, ",
                    f"streamed_responses={[message_to_string(r) for r in self.streamed_responses]})",
                )
            )
        else:
            return message_to_string(error)


class ServerCall(NamedTuple):
    timestamp: datetime
    request: Union[Message, list[Message]]
    metadata: MetadataDict
    result: Union[Message, GrpcStatus]
    end_timestamp: datetime

    @property
    def successful(self) -> bool:
        return not isinstance(self.result, GrpcStatus) or self.result.code is None

    def __str__(self) -> str:
        # request
        if isinstance(self.request, Message):
            request_string = f"request={message_to_string(self.request)}"
        else:
            request_string = f"requests=[{', '.join(message_to_string(m) for m in self.request)}]"

        # result
        if isinstance(self.result, Message):
            result_string = f"response={message_to_string(self.result)}"
        elif self.result.code is None and self.result.details is None:
            result_string = f"responses=[{', '.join(message_to_string(m) for m in self.result.streamed_responses)}]"
        else:
            result_string = f"error={self.result}"

        return "".join(
            (
                self.__class__.__name__,
                "(",
                f"timestamp={self.timestamp!r}, ",
                f"{request_string}, ",
                f"metadata={self.metadata}, ",
                f"{result_string}, ",
                f"end_timestamp={self.end_timestamp!r}",
                ")",
            )
        )


ARGS_DICT: dict[str, list[ServerCall]] = defaultdict(list)


def spy_servicer(servicer):
    for name in dir(servicer):
        binding = getattr(servicer, name)
        if callable(binding) and name[0].isupper():
            setattr(servicer, name, _spy_method(binding))
    return servicer


class SpyRequestIterator(Iterator[T]):
    def __init__(self, request_stream: Iterator[T]):
        self.__request_stream = request_stream
        self.request_list: list[T] = []

    def __next__(self) -> T:
        logger.debug("Polling for next request in stream")
        request = next(self.__request_stream)
        logger.info(f"Next stream request: {message_to_string(request)}")
        self.request_list.append(request)
        return request

    def __iter__(self) -> Iterator[T]:
        return self


def _spy_method(rpc_method):
    @wraps(rpc_method)
    def wrapper(request: Union[Message, Iterator[Message]], context: ServicerContext):
        timestamp = datetime.now()
        method_name = rpc_method.__qualname__.replace("Impl.", ".").replace("Servicer.", ".")

        logger.debug(f"RPC initialized: {method_name}")
        context.add_callback(lambda: logger.debug(f"RPC terminated: {method_name}"))

        if isinstance(request, Message):
            # single request
            logger.info(f"Received request message: {message_to_string(request)}")
        else:
            # request stream
            request = SpyRequestIterator(request)

        metadata = extract_metadata(context)

        def stream_response_handler(stream, wrapped_list):
            try:
                for item in stream:
                    logger.info(f"Sending stream response: {message_to_string(item)}")
                    wrapped_list.append(item)
                    yield item
            except BaseException as ex:
                if repr(ex) != "Exception()":
                    logger.error(f"Exception while iterating responses for {method_name}: {ex!r}")

            summary = ServerCall(
                timestamp,
                request if isinstance(request, Message) else request.request_list,
                metadata,
                result=GrpcStatus(context.code(), context.details(), wrapped_list),
                end_timestamp=datetime.now(),
            )
            ARGS_DICT[method_name].append(summary)

        response: Union[list, Message, GrpcStatus, None] = None
        try:
            grpc_response = rpc_method(request, context)
            if isinstance(grpc_response, types.GeneratorType):
                response = []
                return stream_response_handler(grpc_response, response)
            else:
                response = grpc_response
                ARGS_DICT[method_name].append(
                    ServerCall(timestamp, request, metadata, result=response, end_timestamp=datetime.now())
                )
                logger.info(f"Sending response message: {message_to_string(response)}")
                return grpc_response
        except BaseException:  # server-side errors throw an empty Exception() and modify the context state
            if not isinstance(response, list):
                response = []
            response = GrpcStatus(context.code(), context.details(), response)
            ARGS_DICT[method_name].append(
                ServerCall(timestamp, request, metadata, result=response, end_timestamp=datetime.now())
            )
            logger.error(f"Call failed: {response}")
            raise

    return wrapper


def extract_metadata(context: ServicerContext) -> MetadataDict:
    key: str
    value: bytes
    metadata_messages: list[Message] = []
    for key, value in context.invocation_metadata():
        if not key.startswith("sila-"):
            continue

        logger.debug(f"Parsing metadata: {key} - {value!r}")

        try:
            _, _, _, lowercase_feature_id, _, _, lowercase_metadata_id, _ = key.split("-")
            feature_id, fdl_root = {f: x for (f, x) in fdl_xmls.items() if f.lower() == lowercase_feature_id}.popitem()
            metadata_items: list[str] = xpath_sila(fdl_root, "/sila:Feature/sila:Metadata/sila:Identifier/text()")
            metadata_id = [m for m in metadata_items if m.lower() == lowercase_metadata_id][0]

            message_class = get_message_class(f"{feature_id}.Metadata_{metadata_id}")
            metadata_message = message_class.FromString(value)
            metadata_messages.append(metadata_message)
            logger.info(f"Parsed metadata: {metadata_id} - {message_to_string(metadata_message)}")
        except BaseException as ex:
            logger.warning(f"Failed to parse metadata: {ex!r}")

    return MetadataDict(*metadata_messages)
