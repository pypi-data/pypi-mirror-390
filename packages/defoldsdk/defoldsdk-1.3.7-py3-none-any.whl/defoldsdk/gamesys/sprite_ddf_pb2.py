"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
from defoldsdk.graphics import graphics_ddf_pb2 as graphics_dot_graphics__ddf__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18gamesys/sprite_ddf.proto\x12\x0fdmGameSystemDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto\x1a\x1bgraphics/graphics_ddf.proto"7\n\rSpriteTexture\x12\x0f\n\x07sampler\x18\x01 \x02(\t\x12\x15\n\x07texture\x18\x02 \x02(\tB\x04\xa0\xbb\x18\x01"\xf6\x05\n\nSpriteDesc\x12\x16\n\x08tile_set\x18\x01 \x01(\tB\x04\xa0\xbb\x18\x01\x12\x19\n\x11default_animation\x18\x02 \x02(\t\x12;\n\x08material\x18\x03 \x01(\t:#/builtins/materials/sprite.materialB\x04\xa0\xbb\x18\x01\x12K\n\nblend_mode\x18\x04 \x01(\x0e2%.dmGameSystemDDF.SpriteDesc.BlendMode:\x10BLEND_MODE_ALPHA\x12\x1f\n\x06slice9\x18\x05 \x01(\x0b2\x0f.dmMath.Vector4\x12\x1d\n\x04size\x18\x06 \x01(\x0b2\x0f.dmMath.Vector4\x12G\n\tsize_mode\x18\x07 \x01(\x0e2$.dmGameSystemDDF.SpriteDesc.SizeMode:\x0eSIZE_MODE_AUTO\x12\x11\n\x06offset\x18\x08 \x01(\x02:\x010\x12\x18\n\rplayback_rate\x18\t \x01(\x02:\x011\x12/\n\nattributes\x18\n \x03(\x0b2\x1b.dmGraphics.VertexAttribute\x120\n\x08textures\x18\x0b \x03(\x0b2\x1e.dmGameSystemDDF.SpriteTexture"\xc5\x01\n\tBlendMode\x12\x1f\n\x10BLEND_MODE_ALPHA\x10\x00\x1a\t\xc2\xc1\x18\x05Alpha\x12\x1b\n\x0eBLEND_MODE_ADD\x10\x01\x1a\x07\xc2\xc1\x18\x03Add\x124\n\x14BLEND_MODE_ADD_ALPHA\x10\x02\x1a\x1a\xc2\xc1\x18\x16Add Alpha (Deprecated)\x12!\n\x0fBLEND_MODE_MULT\x10\x03\x1a\x0c\xc2\xc1\x18\x08Multiply\x12!\n\x11BLEND_MODE_SCREEN\x10\x04\x1a\n\xc2\xc1\x18\x06Screen"J\n\x08SizeMode\x12 \n\x10SIZE_MODE_MANUAL\x10\x00\x1a\n\xc2\xc1\x18\x06Manual\x12\x1c\n\x0eSIZE_MODE_AUTO\x10\x01\x1a\x08\xc2\xc1\x18\x04Auto"H\n\rPlayAnimation\x12\n\n\x02id\x18\x01 \x02(\x04\x12\x11\n\x06offset\x18\x02 \x01(\x02:\x010\x12\x18\n\rplayback_rate\x18\x03 \x01(\x02:\x011"1\n\rAnimationDone\x12\x14\n\x0ccurrent_tile\x18\x01 \x02(\r\x12\n\n\x02id\x18\x02 \x02(\x04"!\n\x11SetFlipHorizontal\x12\x0c\n\x04flip\x18\x01 \x02(\r"\x1f\n\x0fSetFlipVertical\x12\x0c\n\x04flip\x18\x01 \x02(\rB"\n\x18com.dynamo.gamesys.protoB\x06Sprite')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gamesys.sprite_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x18com.dynamo.gamesys.protoB\x06Sprite'
    _SPRITETEXTURE.fields_by_name['texture']._options = None
    _SPRITETEXTURE.fields_by_name['texture']._serialized_options = b'\xa0\xbb\x18\x01'
    _SPRITEDESC_BLENDMODE.values_by_name['BLEND_MODE_ALPHA']._options = None
    _SPRITEDESC_BLENDMODE.values_by_name['BLEND_MODE_ALPHA']._serialized_options = b'\xc2\xc1\x18\x05Alpha'
    _SPRITEDESC_BLENDMODE.values_by_name['BLEND_MODE_ADD']._options = None
    _SPRITEDESC_BLENDMODE.values_by_name['BLEND_MODE_ADD']._serialized_options = b'\xc2\xc1\x18\x03Add'
    _SPRITEDESC_BLENDMODE.values_by_name['BLEND_MODE_ADD_ALPHA']._options = None
    _SPRITEDESC_BLENDMODE.values_by_name['BLEND_MODE_ADD_ALPHA']._serialized_options = b'\xc2\xc1\x18\x16Add Alpha (Deprecated)'
    _SPRITEDESC_BLENDMODE.values_by_name['BLEND_MODE_MULT']._options = None
    _SPRITEDESC_BLENDMODE.values_by_name['BLEND_MODE_MULT']._serialized_options = b'\xc2\xc1\x18\x08Multiply'
    _SPRITEDESC_BLENDMODE.values_by_name['BLEND_MODE_SCREEN']._options = None
    _SPRITEDESC_BLENDMODE.values_by_name['BLEND_MODE_SCREEN']._serialized_options = b'\xc2\xc1\x18\x06Screen'
    _SPRITEDESC_SIZEMODE.values_by_name['SIZE_MODE_MANUAL']._options = None
    _SPRITEDESC_SIZEMODE.values_by_name['SIZE_MODE_MANUAL']._serialized_options = b'\xc2\xc1\x18\x06Manual'
    _SPRITEDESC_SIZEMODE.values_by_name['SIZE_MODE_AUTO']._options = None
    _SPRITEDESC_SIZEMODE.values_by_name['SIZE_MODE_AUTO']._serialized_options = b'\xc2\xc1\x18\x04Auto'
    _SPRITEDESC.fields_by_name['tile_set']._options = None
    _SPRITEDESC.fields_by_name['tile_set']._serialized_options = b'\xa0\xbb\x18\x01'
    _SPRITEDESC.fields_by_name['material']._options = None
    _SPRITEDESC.fields_by_name['material']._serialized_options = b'\xa0\xbb\x18\x01'
    _SPRITETEXTURE._serialized_start = 120
    _SPRITETEXTURE._serialized_end = 175
    _SPRITEDESC._serialized_start = 178
    _SPRITEDESC._serialized_end = 936
    _SPRITEDESC_BLENDMODE._serialized_start = 663
    _SPRITEDESC_BLENDMODE._serialized_end = 860
    _SPRITEDESC_SIZEMODE._serialized_start = 862
    _SPRITEDESC_SIZEMODE._serialized_end = 936
    _PLAYANIMATION._serialized_start = 938
    _PLAYANIMATION._serialized_end = 1010
    _ANIMATIONDONE._serialized_start = 1012
    _ANIMATIONDONE._serialized_end = 1061
    _SETFLIPHORIZONTAL._serialized_start = 1063
    _SETFLIPHORIZONTAL._serialized_end = 1096
    _SETFLIPVERTICAL._serialized_start = 1098
    _SETFLIPVERTICAL._serialized_end = 1129
