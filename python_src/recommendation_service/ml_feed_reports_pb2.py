# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: recommendation_service/ml_feed_reports.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    "",
    "recommendation_service/ml_feed_reports.proto",
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n,recommendation_service/ml_feed_reports.proto\x12\x0fml_feed_reports"\xa4\x02\n\x0cMLFeedReport\x12\x18\n\x10reportee_user_id\x18\x01 \x01(\t\x12\x1c\n\x14reportee_canister_id\x18\x02 \x01(\t\x12\x19\n\x11video_canister_id\x18\x03 \x01(\t\x12\x15\n\rvideo_post_id\x18\x04 \x01(\t\x12\x11\n\tvideo_uri\x18\x05 \x01(\t\x12 \n\x18parent_video_canister_id\x18\x06 \x01(\t\x12\x1c\n\x14parent_video_post_id\x18\x07 \x01(\t\x12\x18\n\x10parent_video_uri\x18\x08 \x01(\t\x12\x18\n\x10report_timestamp\x18\t \x01(\t\x12\x13\n\x0breport_type\x18\n \x01(\t\x12\x0e\n\x06reason\x18\x0b \x01(\tb\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "recommendation_service.ml_feed_reports_pb2", _globals
)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_MLFEEDREPORT"]._serialized_start = 66
    _globals["_MLFEEDREPORT"]._serialized_end = 358
# @@protoc_insertion_point(module_scope)
