# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: order.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0border.proto\x12\x05order\"\x95\x01\n\nOrderProto\x12\n\n\x02id\x18\x01 \x01(\t\x12\x11\n\titem_name\x18\x02 \x01(\t\x12\x10\n\x08quantity\x18\x03 \x01(\x05\x12\r\n\x05price\x18\x04 \x01(\x02\x12\x0e\n\x06status\x18\x05 \x01(\t\x12\x12\n\nuser_email\x18\x06 \x01(\t\x12\x12\n\nuser_phone\x18\x07 \x01(\t\x12\x0f\n\x07\x61pi_key\x18\t \x01(\tb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'order_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ORDERPROTO._serialized_start=23
  _ORDERPROTO._serialized_end=172
# @@protoc_insertion_point(module_scope)
