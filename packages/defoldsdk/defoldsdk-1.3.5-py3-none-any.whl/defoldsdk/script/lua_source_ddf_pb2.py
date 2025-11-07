"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bscript/lua_source_ddf.proto\x12\x08dmLuaDDF"x\n\tLuaSource\x12\x0e\n\x06script\x18\x01 \x01(\x0c\x12\x10\n\x08filename\x18\x02 \x02(\t\x12\x10\n\x08bytecode\x18\x03 \x01(\x0c\x12\r\n\x05delta\x18\x05 \x01(\x0c\x12\x13\n\x0bbytecode_32\x18\x06 \x01(\x0c\x12\x13\n\x0bbytecode_64\x18\x04 \x01(\x0cB\x1e\n\x17com.dynamo.script.protoB\x03Lua')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'script.lua_source_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x17com.dynamo.script.protoB\x03Lua'
    _LUASOURCE._serialized_start = 41
    _LUASOURCE._serialized_end = 161
