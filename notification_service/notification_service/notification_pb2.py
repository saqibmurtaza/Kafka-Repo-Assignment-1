# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: notification.proto
# Protobuf Python Version: 5.27.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    1,
    '',
    'notification.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12notification.proto\x12\x0cnotification\"d\n\x18NotificationPayloadProto\x12\x10\n\x08order_id\x18\x01 \x01(\x05\x12\x0e\n\x06status\x18\x02 \x01(\t\x12\x12\n\nuser_email\x18\x03 \x01(\t\x12\x12\n\nuser_phone\x18\x04 \x01(\tb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'notification_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_NOTIFICATIONPAYLOADPROTO']._serialized_start=36
  _globals['_NOTIFICATIONPAYLOADPROTO']._serialized_end=136
# @@protoc_insertion_point(module_scope)