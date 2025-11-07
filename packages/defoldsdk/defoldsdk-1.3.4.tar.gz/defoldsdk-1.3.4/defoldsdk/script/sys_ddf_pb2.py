"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14script/sys_ddf.proto\x12\x0bdmSystemDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"\x14\n\x04Exit\x12\x0c\n\x04code\x18\x01 \x02(\x05"\x0f\n\rToggleProfile"\x14\n\x12TogglePhysicsDebug"J\n\x0bStartRecord\x12\x11\n\tfile_name\x18\x01 \x02(\t\x12\x17\n\x0cframe_period\x18\x02 \x01(\x05:\x012\x12\x0f\n\x03fps\x18\x03 \x01(\x05:\x0230"\x0c\n\nStopRecord"\\\n\x06Reboot\x12\x0c\n\x04arg1\x18\x01 \x01(\t\x12\x0c\n\x04arg2\x18\x02 \x01(\t\x12\x0c\n\x04arg3\x18\x03 \x01(\t\x12\x0c\n\x04arg4\x18\x04 \x01(\t\x12\x0c\n\x04arg5\x18\x05 \x01(\t\x12\x0c\n\x04arg6\x18\x06 \x01(\t"$\n\x08SetVsync\x12\x18\n\rswap_interval\x18\x01 \x02(\x05:\x011"\'\n\x12SetUpdateFrequency\x12\x11\n\tfrequency\x18\x01 \x02(\x05"\x11\n\x0fResumeRenderingB!\n\x17com.dynamo.system.protoB\x06System')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'script.sys_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x17com.dynamo.system.protoB\x06System'
    _EXIT._serialized_start = 83
    _EXIT._serialized_end = 103
    _TOGGLEPROFILE._serialized_start = 105
    _TOGGLEPROFILE._serialized_end = 120
    _TOGGLEPHYSICSDEBUG._serialized_start = 122
    _TOGGLEPHYSICSDEBUG._serialized_end = 142
    _STARTRECORD._serialized_start = 144
    _STARTRECORD._serialized_end = 218
    _STOPRECORD._serialized_start = 220
    _STOPRECORD._serialized_end = 232
    _REBOOT._serialized_start = 234
    _REBOOT._serialized_end = 326
    _SETVSYNC._serialized_start = 328
    _SETVSYNC._serialized_end = 364
    _SETUPDATEFREQUENCY._serialized_start = 366
    _SETUPDATEFREQUENCY._serialized_end = 405
    _RESUMERENDERING._serialized_start = 407
    _RESUMERENDERING._serialized_end = 424
