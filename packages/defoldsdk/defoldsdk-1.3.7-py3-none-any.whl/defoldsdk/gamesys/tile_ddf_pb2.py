"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16gamesys/tile_ddf.proto\x12\x0fdmGameSystemDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"O\n\nConvexHull\x12\x10\n\x05index\x18\x01 \x02(\r:\x010\x12\x10\n\x05count\x18\x02 \x02(\r:\x010\x12\x1d\n\x0fcollision_group\x18\x03 \x02(\t:\x04tile"2\n\x03Cue\x12\n\n\x02id\x18\x01 \x02(\t\x12\r\n\x05frame\x18\x02 \x02(\r\x12\x10\n\x05value\x18\x03 \x01(\x02:\x010"\xec\x01\n\tAnimation\x12\n\n\x02id\x18\x01 \x02(\t\x12\x12\n\nstart_tile\x18\x02 \x02(\r\x12\x10\n\x08end_tile\x18\x03 \x02(\r\x12B\n\x08playback\x18\x04 \x01(\x0e2\x19.dmGameSystemDDF.Playback:\x15PLAYBACK_ONCE_FORWARD\x12\x0f\n\x03fps\x18\x05 \x01(\r:\x0230\x12\x1a\n\x0fflip_horizontal\x18\x06 \x01(\r:\x010\x12\x18\n\rflip_vertical\x18\x07 \x01(\r:\x010\x12"\n\x04cues\x18\x08 \x03(\x0b2\x14.dmGameSystemDDF.Cue"\xdd\x03\n\x07TileSet\x12\x13\n\x05image\x18\x01 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x15\n\ntile_width\x18\x02 \x02(\r:\x010\x12\x16\n\x0btile_height\x18\x03 \x02(\r:\x010\x12\x16\n\x0btile_margin\x18\x04 \x01(\r:\x010\x12\x17\n\x0ctile_spacing\x18\x05 \x01(\r:\x010\x12\x17\n\tcollision\x18\x06 \x01(\tB\x04\xa0\xbb\x18\x01\x12\x1a\n\x0cmaterial_tag\x18\x07 \x01(\t:\x04tile\x121\n\x0cconvex_hulls\x18\x08 \x03(\x0b2\x1b.dmGameSystemDDF.ConvexHull\x12 \n\x12convex_hull_points\x18\t \x03(\x02B\x04\xa8\xbb\x18\x01\x12\x18\n\x10collision_groups\x18\n \x03(\t\x12.\n\nanimations\x18\x0b \x03(\x0b2\x1a.dmGameSystemDDF.Animation\x12\x1a\n\x0fextrude_borders\x18\x0c \x01(\r:\x010\x12\x18\n\rinner_padding\x18\r \x01(\r:\x010\x12S\n\x10sprite_trim_mode\x18\x0e \x01(\x0e2#.dmGameSystemDDF.SpriteTrimmingMode:\x14SPRITE_TRIM_MODE_OFF"r\n\x08TileCell\x12\x0c\n\x01x\x18\x01 \x02(\x05:\x010\x12\x0c\n\x01y\x18\x02 \x02(\x05:\x010\x12\x0f\n\x04tile\x18\x03 \x02(\r:\x010\x12\x11\n\x06h_flip\x18\x04 \x01(\r:\x010\x12\x11\n\x06v_flip\x18\x05 \x01(\r:\x010\x12\x13\n\x08rotate90\x18\x06 \x01(\r:\x010"\x87\x01\n\tTileLayer\x12\x12\n\x02id\x18\x01 \x02(\t:\x06layer1\x12\x0c\n\x01z\x18\x02 \x02(\x02:\x010\x12\x15\n\nis_visible\x18\x03 \x01(\r:\x011\x12\x18\n\x07id_hash\x18\x04 \x01(\x04:\x010B\x04\xa8\xbb\x18\x01\x12\'\n\x04cell\x18\x06 \x03(\x0b2\x19.dmGameSystemDDF.TileCell"\xa0\x03\n\x08TileGrid\x12\x16\n\x08tile_set\x18\x01 \x02(\tB\x04\xa0\xbb\x18\x01\x12*\n\x06layers\x18\x02 \x03(\x0b2\x1a.dmGameSystemDDF.TileLayer\x12=\n\x08material\x18\x03 \x01(\t:%/builtins/materials/tile_map.materialB\x04\xa0\xbb\x18\x01\x12I\n\nblend_mode\x18\x04 \x01(\x0e2#.dmGameSystemDDF.TileGrid.BlendMode:\x10BLEND_MODE_ALPHA"\xc5\x01\n\tBlendMode\x12\x1f\n\x10BLEND_MODE_ALPHA\x10\x00\x1a\t\xc2\xc1\x18\x05Alpha\x12\x1b\n\x0eBLEND_MODE_ADD\x10\x01\x1a\x07\xc2\xc1\x18\x03Add\x124\n\x14BLEND_MODE_ADD_ALPHA\x10\x02\x1a\x1a\xc2\xc1\x18\x16Add Alpha (Deprecated)\x12!\n\x0fBLEND_MODE_MULT\x10\x03\x1a\x0c\xc2\xc1\x18\x08Multiply\x12!\n\x11BLEND_MODE_SCREEN\x10\x04\x1a\n\xc2\xc1\x18\x06Screen"M\n\x12SetConstantTileMap\x12\x11\n\tname_hash\x18\x01 \x02(\x04\x12$\n\x05value\x18\x02 \x02(\x0b2\x0f.dmMath.Vector4B\x04\xa0\xb5\x18\x01")\n\x14ResetConstantTileMap\x12\x11\n\tname_hash\x18\x01 \x02(\x04*\xbf\x02\n\x08Playback\x12\x1b\n\rPLAYBACK_NONE\x10\x00\x1a\x08\xc2\xc1\x18\x04None\x12+\n\x15PLAYBACK_ONCE_FORWARD\x10\x01\x1a\x10\xc2\xc1\x18\x0cOnce Forward\x12-\n\x16PLAYBACK_ONCE_BACKWARD\x10\x02\x1a\x11\xc2\xc1\x18\rOnce Backward\x12.\n\x16PLAYBACK_ONCE_PINGPONG\x10\x06\x1a\x12\xc2\xc1\x18\x0eOnce Ping Pong\x12+\n\x15PLAYBACK_LOOP_FORWARD\x10\x03\x1a\x10\xc2\xc1\x18\x0cLoop Forward\x12-\n\x16PLAYBACK_LOOP_BACKWARD\x10\x04\x1a\x11\xc2\xc1\x18\rLoop Backward\x12.\n\x16PLAYBACK_LOOP_PINGPONG\x10\x05\x1a\x12\xc2\xc1\x18\x0eLoop Ping Pong*\xa7\x02\n\x12SpriteTrimmingMode\x12!\n\x14SPRITE_TRIM_MODE_OFF\x10\x00\x1a\x07\xc2\xc1\x18\x03Off\x12&\n\x12SPRITE_TRIM_MODE_4\x10\x04\x1a\x0e\xc2\xc1\x18\n4 Vertices\x12&\n\x12SPRITE_TRIM_MODE_5\x10\x05\x1a\x0e\xc2\xc1\x18\n5 Vertices\x12&\n\x12SPRITE_TRIM_MODE_6\x10\x06\x1a\x0e\xc2\xc1\x18\n6 Vertices\x12&\n\x12SPRITE_TRIM_MODE_7\x10\x07\x1a\x0e\xc2\xc1\x18\n7 Vertices\x12&\n\x12SPRITE_TRIM_MODE_8\x10\x08\x1a\x0e\xc2\xc1\x18\n8 Vertices\x12&\n\x14SPRITE_TRIM_POLYGONS\x10\t\x1a\x0c\xc2\xc1\x18\x08PolygonsB \n\x18com.dynamo.gamesys.protoB\x04Tile')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gamesys.tile_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x18com.dynamo.gamesys.protoB\x04Tile'
    _PLAYBACK.values_by_name['PLAYBACK_NONE']._options = None
    _PLAYBACK.values_by_name['PLAYBACK_NONE']._serialized_options = b'\xc2\xc1\x18\x04None'
    _PLAYBACK.values_by_name['PLAYBACK_ONCE_FORWARD']._options = None
    _PLAYBACK.values_by_name['PLAYBACK_ONCE_FORWARD']._serialized_options = b'\xc2\xc1\x18\x0cOnce Forward'
    _PLAYBACK.values_by_name['PLAYBACK_ONCE_BACKWARD']._options = None
    _PLAYBACK.values_by_name['PLAYBACK_ONCE_BACKWARD']._serialized_options = b'\xc2\xc1\x18\rOnce Backward'
    _PLAYBACK.values_by_name['PLAYBACK_ONCE_PINGPONG']._options = None
    _PLAYBACK.values_by_name['PLAYBACK_ONCE_PINGPONG']._serialized_options = b'\xc2\xc1\x18\x0eOnce Ping Pong'
    _PLAYBACK.values_by_name['PLAYBACK_LOOP_FORWARD']._options = None
    _PLAYBACK.values_by_name['PLAYBACK_LOOP_FORWARD']._serialized_options = b'\xc2\xc1\x18\x0cLoop Forward'
    _PLAYBACK.values_by_name['PLAYBACK_LOOP_BACKWARD']._options = None
    _PLAYBACK.values_by_name['PLAYBACK_LOOP_BACKWARD']._serialized_options = b'\xc2\xc1\x18\rLoop Backward'
    _PLAYBACK.values_by_name['PLAYBACK_LOOP_PINGPONG']._options = None
    _PLAYBACK.values_by_name['PLAYBACK_LOOP_PINGPONG']._serialized_options = b'\xc2\xc1\x18\x0eLoop Ping Pong'
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_MODE_OFF']._options = None
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_MODE_OFF']._serialized_options = b'\xc2\xc1\x18\x03Off'
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_MODE_4']._options = None
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_MODE_4']._serialized_options = b'\xc2\xc1\x18\n4 Vertices'
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_MODE_5']._options = None
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_MODE_5']._serialized_options = b'\xc2\xc1\x18\n5 Vertices'
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_MODE_6']._options = None
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_MODE_6']._serialized_options = b'\xc2\xc1\x18\n6 Vertices'
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_MODE_7']._options = None
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_MODE_7']._serialized_options = b'\xc2\xc1\x18\n7 Vertices'
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_MODE_8']._options = None
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_MODE_8']._serialized_options = b'\xc2\xc1\x18\n8 Vertices'
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_POLYGONS']._options = None
    _SPRITETRIMMINGMODE.values_by_name['SPRITE_TRIM_POLYGONS']._serialized_options = b'\xc2\xc1\x18\x08Polygons'
    _TILESET.fields_by_name['image']._options = None
    _TILESET.fields_by_name['image']._serialized_options = b'\xa0\xbb\x18\x01'
    _TILESET.fields_by_name['collision']._options = None
    _TILESET.fields_by_name['collision']._serialized_options = b'\xa0\xbb\x18\x01'
    _TILESET.fields_by_name['convex_hull_points']._options = None
    _TILESET.fields_by_name['convex_hull_points']._serialized_options = b'\xa8\xbb\x18\x01'
    _TILELAYER.fields_by_name['id_hash']._options = None
    _TILELAYER.fields_by_name['id_hash']._serialized_options = b'\xa8\xbb\x18\x01'
    _TILEGRID_BLENDMODE.values_by_name['BLEND_MODE_ALPHA']._options = None
    _TILEGRID_BLENDMODE.values_by_name['BLEND_MODE_ALPHA']._serialized_options = b'\xc2\xc1\x18\x05Alpha'
    _TILEGRID_BLENDMODE.values_by_name['BLEND_MODE_ADD']._options = None
    _TILEGRID_BLENDMODE.values_by_name['BLEND_MODE_ADD']._serialized_options = b'\xc2\xc1\x18\x03Add'
    _TILEGRID_BLENDMODE.values_by_name['BLEND_MODE_ADD_ALPHA']._options = None
    _TILEGRID_BLENDMODE.values_by_name['BLEND_MODE_ADD_ALPHA']._serialized_options = b'\xc2\xc1\x18\x16Add Alpha (Deprecated)'
    _TILEGRID_BLENDMODE.values_by_name['BLEND_MODE_MULT']._options = None
    _TILEGRID_BLENDMODE.values_by_name['BLEND_MODE_MULT']._serialized_options = b'\xc2\xc1\x18\x08Multiply'
    _TILEGRID_BLENDMODE.values_by_name['BLEND_MODE_SCREEN']._options = None
    _TILEGRID_BLENDMODE.values_by_name['BLEND_MODE_SCREEN']._serialized_options = b'\xc2\xc1\x18\x06Screen'
    _TILEGRID.fields_by_name['tile_set']._options = None
    _TILEGRID.fields_by_name['tile_set']._serialized_options = b'\xa0\xbb\x18\x01'
    _TILEGRID.fields_by_name['material']._options = None
    _TILEGRID.fields_by_name['material']._serialized_options = b'\xa0\xbb\x18\x01'
    _SETCONSTANTTILEMAP.fields_by_name['value']._options = None
    _SETCONSTANTTILEMAP.fields_by_name['value']._serialized_options = b'\xa0\xb5\x18\x01'
    _PLAYBACK._serialized_start = 1737
    _PLAYBACK._serialized_end = 2056
    _SPRITETRIMMINGMODE._serialized_start = 2059
    _SPRITETRIMMINGMODE._serialized_end = 2354
    _CONVEXHULL._serialized_start = 89
    _CONVEXHULL._serialized_end = 168
    _CUE._serialized_start = 170
    _CUE._serialized_end = 220
    _ANIMATION._serialized_start = 223
    _ANIMATION._serialized_end = 459
    _TILESET._serialized_start = 462
    _TILESET._serialized_end = 939
    _TILECELL._serialized_start = 941
    _TILECELL._serialized_end = 1055
    _TILELAYER._serialized_start = 1058
    _TILELAYER._serialized_end = 1193
    _TILEGRID._serialized_start = 1196
    _TILEGRID._serialized_end = 1612
    _TILEGRID_BLENDMODE._serialized_start = 1415
    _TILEGRID_BLENDMODE._serialized_end = 1612
    _SETCONSTANTTILEMAP._serialized_start = 1614
    _SETCONSTANTTILEMAP._serialized_end = 1691
    _RESETCONSTANTTILEMAP._serialized_start = 1693
    _RESETCONSTANTTILEMAP._serialized_end = 1734
