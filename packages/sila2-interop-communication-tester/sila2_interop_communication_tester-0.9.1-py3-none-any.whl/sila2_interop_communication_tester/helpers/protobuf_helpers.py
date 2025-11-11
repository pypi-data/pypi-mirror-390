from __future__ import annotations

import sys
import uuid
from importlib import import_module
from pathlib import Path
from typing import Type

from google.protobuf import descriptor_pool
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.descriptor_pb2 import (
    DescriptorProto,
    FieldDescriptorProto,
    FileDescriptorProto,
)
from google.protobuf.message import Message
from google.protobuf.reflection import message_factory
from google.protobuf.text_format import MessageToString

import sila2_interop_communication_tester
from sila2_interop_communication_tester.grpc_stubs.SiLAFramework_pb2 import Any

pb2_dir = Path(sila2_interop_communication_tester.__file__).parent / "grpc_stubs"
pb2_files: dict[str, Path] = {f.name.removeprefix("_pb2.py"): f.absolute() for f in pb2_dir.glob("*_pb2.py")}


def get_message_class(message_id: str) -> Type[Message]:
    """Call with parameters like 'SiLAFramework.Integer' or SiLABinaryTransfer.GetBinaryInfoRequest"""
    proto_name, message_name = message_id.split(".")
    sys.path.append(str(pb2_dir.absolute()))
    try:
        proto_module = import_module(
            f".{proto_name}_pb2", package=sila2_interop_communication_tester.grpc_stubs.__name__
        )
        return getattr(proto_module, message_name)
    finally:
        sys.path.pop()


def message_to_string(message: Message) -> str:
    body = MessageToString(message, as_one_line=True, use_index_order=True)
    if len(body) > 1000:
        body = body[:100] + f"[[omitted {len(body) - 200} chars]]" + body[-100:]
    return message.__class__.__qualname__ + "(" + body + ")"


def create_any_message(type_xml: str, value: Message | list[Message]) -> Any:
    # avoid naming collisions by putting each created type in a different package
    package_name = f"any_{uuid.uuid4().hex.replace('-', '_')}"

    message_name = "AnyMessage"
    field_name = "innerMessage"
    message_identifier = f"{package_name}.{message_name}"

    if isinstance(value, list):
        inner_field_label = FieldDescriptor.LABEL_REPEATED
        inner_field_type_name = value[0].DESCRIPTOR.full_name
    else:
        inner_field_label = FieldDescriptor.LABEL_OPTIONAL
        inner_field_type_name = value.DESCRIPTOR.full_name

    outer_message_proto = DescriptorProto(
        name=message_name,
        field=[
            FieldDescriptorProto(
                name=field_name,
                number=1,
                type=FieldDescriptor.TYPE_MESSAGE,
                type_name=inner_field_type_name,
                label=inner_field_label,
            )
        ],
    )
    file_descriptor_proto = FileDescriptorProto(
        package=package_name,
        name=f"{package_name}.proto",
        message_type=[outer_message_proto],
    )

    pool = descriptor_pool.Default()
    pool.Add(file_descriptor_proto)
    outer_message_descriptor = pool.FindMessageTypeByName(message_identifier)

    outer_message_cls = message_factory.GetMessageClass(outer_message_descriptor)
    return Any(
        type=type_xml, payload=outer_message_cls(innerMessage=value).SerializeToString()
    )
