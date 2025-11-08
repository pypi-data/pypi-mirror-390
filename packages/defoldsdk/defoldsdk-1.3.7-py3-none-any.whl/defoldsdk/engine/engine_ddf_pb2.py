"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
from defoldsdk.gameobject import lua_ddf_pb2 as gameobject_dot_lua__ddf__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17engine/engine_ddf.proto\x12\x0bdmEngineDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto\x1a\x18gameobject/lua_ddf.proto"\t\n\x07HideApp"0\n\tRunScript\x12#\n\x06module\x18\x01 \x02(\x0b2\x13.dmLuaDDF.LuaModuleB!\n\x17com.dynamo.engine.protoB\x06Engine')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'engine.engine_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x17com.dynamo.engine.protoB\x06Engine'
    _HIDEAPP._serialized_start = 112
    _HIDEAPP._serialized_end = 121
    _RUNSCRIPT._serialized_start = 123
    _RUNSCRIPT._serialized_end = 171
