"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18gamesys/buffer_ddf.proto\x12\x0bdmBufferDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"\xab\x01\n\nStreamDesc\x12\x0c\n\x04name\x18\x01 \x02(\t\x12*\n\nvalue_type\x18\x02 \x02(\x0e2\x16.dmBufferDDF.ValueType\x12\x13\n\x0bvalue_count\x18\x03 \x02(\r\x12\n\n\x02ui\x18\x04 \x03(\r\x12\t\n\x01i\x18\x05 \x03(\x05\x12\x0c\n\x04ui64\x18\x06 \x03(\x04\x12\x0b\n\x03i64\x18\x07 \x03(\x03\x12\t\n\x01f\x18\x08 \x03(\x02\x12\x11\n\tname_hash\x18\t \x02(\x04"6\n\nBufferDesc\x12(\n\x07streams\x18\x01 \x03(\x0b2\x17.dmBufferDDF.StreamDesc*\xd5\x01\n\tValueType\x12\x14\n\x10VALUE_TYPE_UINT8\x10\x00\x12\x15\n\x11VALUE_TYPE_UINT16\x10\x01\x12\x15\n\x11VALUE_TYPE_UINT32\x10\x02\x12\x15\n\x11VALUE_TYPE_UINT64\x10\x03\x12\x13\n\x0fVALUE_TYPE_INT8\x10\x04\x12\x14\n\x10VALUE_TYPE_INT16\x10\x05\x12\x14\n\x10VALUE_TYPE_INT32\x10\x06\x12\x14\n\x10VALUE_TYPE_INT64\x10\x07\x12\x16\n\x12VALUE_TYPE_FLOAT32\x10\x08B\'\n\x18com.dynamo.gamesys.protoB\x0bBufferProto')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gamesys.buffer_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x18com.dynamo.gamesys.protoB\x0bBufferProto'
    _VALUETYPE._serialized_start = 318
    _VALUETYPE._serialized_end = 531
    _STREAMDESC._serialized_start = 88
    _STREAMDESC._serialized_end = 259
    _BUFFERDESC._serialized_start = 261
    _BUFFERDESC._serialized_end = 315
