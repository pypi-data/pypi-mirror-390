"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
from defoldsdk.gamesys import tile_ddf_pb2 as gamesys_dot_tile__ddf__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dgamesys/texture_set_ddf.proto\x12\x0fdmGameSystemDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto\x1a\x16gamesys/tile_ddf.proto"\xe7\x01\n\x13TextureSetAnimation\x12\n\n\x02id\x18\x01 \x02(\t\x12\r\n\x05width\x18\x02 \x02(\r\x12\x0e\n\x06height\x18\x03 \x02(\r\x12\r\n\x05start\x18\x04 \x02(\r\x12\x0b\n\x03end\x18\x05 \x02(\r\x12\x0f\n\x03fps\x18\x06 \x01(\r:\x0230\x12B\n\x08playback\x18\x07 \x01(\x0e2\x19.dmGameSystemDDF.Playback:\x15PLAYBACK_ONCE_FORWARD\x12\x1a\n\x0fflip_horizontal\x18\x08 \x01(\r:\x010\x12\x18\n\rflip_vertical\x18\t \x01(\r:\x010"\x8a\x02\n\x0eSpriteGeometry\x12\r\n\x05width\x18\x01 \x02(\r\x12\x0e\n\x06height\x18\x02 \x02(\r\x12\x10\n\x08center_x\x18\x03 \x02(\x02\x12\x10\n\x08center_y\x18\x04 \x02(\x02\x12\x0f\n\x07rotated\x18\x05 \x02(\x08\x12L\n\ttrim_mode\x18\x06 \x02(\x0e2#.dmGameSystemDDF.SpriteTrimmingMode:\x14SPRITE_TRIM_MODE_OFF\x12\x10\n\x08vertices\x18\x07 \x03(\x02\x12\x0b\n\x03uvs\x18\x08 \x03(\x02\x12\x0f\n\x07indices\x18\t \x03(\r\x12\x12\n\x07pivot_x\x18\n \x01(\x02:\x010\x12\x12\n\x07pivot_y\x18\x0b \x01(\x02:\x010"\x8d\x04\n\nTextureSet\x12\x15\n\x07texture\x18\x01 \x02(\tB\x04\xa0\xbb\x18\x01\x12\r\n\x05width\x18\x02 \x02(\r\x12\x0e\n\x06height\x18\x03 \x02(\r\x12\x14\n\x0ctexture_hash\x18\x04 \x01(\x04\x128\n\nanimations\x18\x05 \x03(\x0b2$.dmGameSystemDDF.TextureSetAnimation\x12\x12\n\ntile_width\x18\x06 \x01(\r\x12\x13\n\x0btile_height\x18\x07 \x01(\r\x12\x12\n\ntile_count\x18\x08 \x01(\r\x12\x1d\n\x15collision_hull_points\x18\t \x03(\x02\x12\x18\n\x10collision_groups\x18\n \x03(\t\x121\n\x0cconvex_hulls\x18\x0b \x03(\x0b2\x1b.dmGameSystemDDF.ConvexHull\x12\x19\n\x11image_name_hashes\x18\x0c \x03(\x04\x12\x15\n\rframe_indices\x18\r \x03(\r\x12\x12\n\ntex_coords\x18\x0e \x02(\x0c\x12\x10\n\x08tex_dims\x18\x0f \x01(\x0c\x123\n\ngeometries\x18\x10 \x03(\x0b2\x1f.dmGameSystemDDF.SpriteGeometry\x12\x16\n\x0euse_geometries\x18\x11 \x01(\r\x12\x14\n\x0cpage_indices\x18\x12 \x03(\r\x12\x15\n\npage_count\x18\x13 \x01(\r:\x010B+\n\x18com.dynamo.gamesys.protoB\x0fTextureSetProto')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gamesys.texture_set_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x18com.dynamo.gamesys.protoB\x0fTextureSetProto'
    _TEXTURESET.fields_by_name['texture']._options = None
    _TEXTURESET.fields_by_name['texture']._serialized_options = b'\xa0\xbb\x18\x01'
    _TEXTURESETANIMATION._serialized_start = 121
    _TEXTURESETANIMATION._serialized_end = 352
    _SPRITEGEOMETRY._serialized_start = 355
    _SPRITEGEOMETRY._serialized_end = 621
    _TEXTURESET._serialized_start = 624
    _TEXTURESET._serialized_end = 1149
