"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
from defoldsdk.gamesys import tile_ddf_pb2 as gamesys_dot_tile__ddf__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17gamesys/atlas_ddf.proto\x12\x0fdmGameSystemDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto\x1a\x16gamesys/tile_ddf.proto"\xa2\x01\n\nAtlasImage\x12\x13\n\x05image\x18\x01 \x02(\tB\x04\xa0\xbb\x18\x01\x12S\n\x10sprite_trim_mode\x18\x02 \x01(\x0e2#.dmGameSystemDDF.SpriteTrimmingMode:\x14SPRITE_TRIM_MODE_OFF\x12\x14\n\x07pivot_x\x18\x03 \x01(\x02:\x030.5\x12\x14\n\x07pivot_y\x18\x04 \x01(\x02:\x030.5"\xd4\x01\n\x0eAtlasAnimation\x12\n\n\x02id\x18\x01 \x02(\t\x12+\n\x06images\x18\x02 \x03(\x0b2\x1b.dmGameSystemDDF.AtlasImage\x12B\n\x08playback\x18\x03 \x01(\x0e2\x19.dmGameSystemDDF.Playback:\x15PLAYBACK_ONCE_FORWARD\x12\x0f\n\x03fps\x18\x04 \x01(\r:\x0230\x12\x1a\n\x0fflip_horizontal\x18\x05 \x01(\r:\x010\x12\x18\n\rflip_vertical\x18\x06 \x01(\r:\x010"\x82\x02\n\x05Atlas\x12+\n\x06images\x18\x01 \x03(\x0b2\x1b.dmGameSystemDDF.AtlasImage\x123\n\nanimations\x18\x02 \x03(\x0b2\x1f.dmGameSystemDDF.AtlasAnimation\x12\x11\n\x06margin\x18\x03 \x01(\r:\x010\x12\x1a\n\x0fextrude_borders\x18\x04 \x01(\r:\x010\x12\x18\n\rinner_padding\x18\x05 \x01(\r:\x010\x12\x19\n\x0emax_page_width\x18\x06 \x01(\r:\x010\x12\x1a\n\x0fmax_page_height\x18\x07 \x01(\r:\x010\x12\x17\n\x0frename_patterns\x18\x08 \x01(\tB&\n\x18com.dynamo.gamesys.protoB\nAtlasProto')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gamesys.atlas_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x18com.dynamo.gamesys.protoB\nAtlasProto'
    _ATLASIMAGE.fields_by_name['image']._options = None
    _ATLASIMAGE.fields_by_name['image']._serialized_options = b'\xa0\xbb\x18\x01'
    _ATLASIMAGE._serialized_start = 115
    _ATLASIMAGE._serialized_end = 277
    _ATLASANIMATION._serialized_start = 280
    _ATLASANIMATION._serialized_end = 492
    _ATLAS._serialized_start = 495
    _ATLAS._serialized_end = 753
