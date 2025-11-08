"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17gamesys/sound_ddf.proto\x12\ndmSoundDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"\x94\x01\n\tSoundDesc\x12\x13\n\x05sound\x18\x01 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x12\n\x07looping\x18\x02 \x01(\x05:\x010\x12\x15\n\x05group\x18\x03 \x01(\t:\x06master\x12\x0f\n\x04gain\x18\x04 \x01(\x02:\x011\x12\x0e\n\x03pan\x18\x05 \x01(\x02:\x010\x12\x10\n\x05speed\x18\x06 \x01(\x02:\x011\x12\x14\n\tloopcount\x18\x07 \x01(\x05:\x010B!\n\x18com.dynamo.gamesys.protoB\x05Sound')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gamesys.sound_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x18com.dynamo.gamesys.protoB\x05Sound'
    _SOUNDDESC.fields_by_name['sound']._options = None
    _SOUNDDESC.fields_by_name['sound']._serialized_options = b'\xa0\xbb\x18\x01'
    _SOUNDDESC._serialized_start = 86
    _SOUNDDESC._serialized_end = 234
