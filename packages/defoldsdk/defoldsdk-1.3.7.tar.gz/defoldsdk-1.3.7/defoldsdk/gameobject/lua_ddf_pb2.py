"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
from defoldsdk.script import lua_source_ddf_pb2 as script_dot_lua__source__ddf__pb2
from defoldsdk.gameobject import properties_ddf_pb2 as gameobject_dot_properties__ddf__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18gameobject/lua_ddf.proto\x12\x08dmLuaDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto\x1a\x1bscript/lua_source_ddf.proto\x1a\x1fgameobject/properties_ddf.proto"\xb7\x01\n\tLuaModule\x12#\n\x06source\x18\x01 \x02(\x0b2\x13.dmLuaDDF.LuaSource\x12\x0f\n\x07modules\x18\x02 \x03(\t\x12\x17\n\tresources\x18\x03 \x03(\tB\x04\xa0\xbb\x18\x01\x129\n\nproperties\x18\x04 \x01(\x0b2%.dmPropertiesDDF.PropertyDeclarations\x12 \n\x12property_resources\x18\x05 \x03(\tB\x04\xa0\xbb\x18\x01B\x1b\n\x14com.dynamo.lua.protoB\x03Lua')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gameobject.lua_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x14com.dynamo.lua.protoB\x03Lua'
    _LUAMODULE.fields_by_name['resources']._options = None
    _LUAMODULE.fields_by_name['resources']._serialized_options = b'\xa0\xbb\x18\x01'
    _LUAMODULE.fields_by_name['property_resources']._options = None
    _LUAMODULE.fields_by_name['property_resources']._serialized_options = b'\xa0\xbb\x18\x01'
    _LUAMODULE._serialized_start = 147
    _LUAMODULE._serialized_end = 330
