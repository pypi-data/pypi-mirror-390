"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from google.protobuf import descriptor_pb2 as google_dot_protobuf_dot_descriptor__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18ddf/ddf_extensions.proto\x1a google/protobuf/descriptor.proto:0\n\x05alias\x12\x1f.google.protobuf.MessageOptions\x18\xd0\x86\x03 \x01(\t:7\n\x0cstruct_align\x12\x1f.google.protobuf.MessageOptions\x18\xd3\x86\x03 \x01(\x08:1\n\x08resource\x12\x1d.google.protobuf.FieldOptions\x18\xb4\x87\x03 \x01(\x08:5\n\x0cruntime_only\x12\x1d.google.protobuf.FieldOptions\x18\xb5\x87\x03 \x01(\x08:4\n\x0bfield_align\x12\x1d.google.protobuf.FieldOptions\x18\xd4\x86\x03 \x01(\x08:8\n\x0bdisplayName\x12!.google.protobuf.EnumValueOptions\x18\x98\x88\x03 \x01(\t:5\n\rddf_namespace\x12\x1c.google.protobuf.FileOptions\x18\xd1\x86\x03 \x01(\t:4\n\x0cddf_includes\x12\x1c.google.protobuf.FileOptions\x18\xd2\x86\x03 \x01(\tB!\n\x10com.dynamo.protoB\rDdfExtensions')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ddf.ddf_extensions_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(alias)
    google_dot_protobuf_dot_descriptor__pb2.MessageOptions.RegisterExtension(struct_align)
    google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(resource)
    google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(runtime_only)
    google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(field_align)
    google_dot_protobuf_dot_descriptor__pb2.EnumValueOptions.RegisterExtension(displayName)
    google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(ddf_namespace)
    google_dot_protobuf_dot_descriptor__pb2.FileOptions.RegisterExtension(ddf_includes)
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x10com.dynamo.protoB\rDdfExtensions'
