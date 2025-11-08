"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
from defoldsdk.graphics import graphics_ddf_pb2 as graphics_dot_graphics__ddf__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17gamesys/model_ddf.proto\x12\ndmModelDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto\x1a\x1bgraphics/graphics_ddf.proto"1\n\x07Texture\x12\x0f\n\x07sampler\x18\x01 \x02(\t\x12\x15\n\x07texture\x18\x02 \x02(\tB\x04\xa0\xbb\x18\x01"\x88\x01\n\x08Material\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x16\n\x08material\x18\x02 \x02(\tB\x04\xa0\xbb\x18\x01\x12%\n\x08textures\x18\x03 \x03(\x0b2\x13.dmModelDDF.Texture\x12/\n\nattributes\x18\x04 \x03(\x0b2\x1b.dmGraphics.VertexAttribute"\xf2\x01\n\tModelDesc\x12\x12\n\x04mesh\x18\x02 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x16\n\x08material\x18\x03 \x01(\tB\x04\xa0\xbb\x18\x01\x12\x16\n\x08textures\x18\x04 \x03(\tB\x04\xa0\xbb\x18\x01\x12\x16\n\x08skeleton\x18\x05 \x01(\tB\x04\xa0\xbb\x18\x01\x12\x18\n\nanimations\x18\x06 \x01(\tB\x04\xa0\xbb\x18\x01\x12\x19\n\x11default_animation\x18\x07 \x01(\t\x12\x0c\n\x04name\x18\n \x01(\t\x12\'\n\tmaterials\x18\x0b \x03(\x0b2\x14.dmModelDDF.Material\x12\x1d\n\x0fcreate_go_bones\x18\x0c \x01(\x08:\x04true"}\n\x05Model\x12\x17\n\trig_scene\x18\x01 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x19\n\x11default_animation\x18\x02 \x01(\t\x12\'\n\tmaterials\x18\x03 \x03(\x0b2\x14.dmModelDDF.Material\x12\x17\n\x0fcreate_go_bones\x18\x04 \x01(\x08""\n\rResetConstant\x12\x11\n\tname_hash\x18\x01 \x02(\x04"8\n\nSetTexture\x12\x14\n\x0ctexture_hash\x18\x01 \x02(\x04\x12\x14\n\x0ctexture_unit\x18\x02 \x02(\r"\x84\x01\n\x12ModelPlayAnimation\x12\x14\n\x0canimation_id\x18\x01 \x02(\x04\x12\x10\n\x08playback\x18\x02 \x02(\r\x12\x19\n\x0eblend_duration\x18\x03 \x01(\x02:\x010\x12\x11\n\x06offset\x18\x04 \x01(\x02:\x010\x12\x18\n\rplayback_rate\x18\x05 \x01(\x02:\x011"\x16\n\x14ModelCancelAnimation"<\n\x12ModelAnimationDone\x12\x14\n\x0canimation_id\x18\x01 \x02(\x04\x12\x10\n\x08playback\x18\x02 \x02(\rB&\n\x18com.dynamo.gamesys.protoB\nModelProto')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gamesys.model_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x18com.dynamo.gamesys.protoB\nModelProto'
    _TEXTURE.fields_by_name['texture']._options = None
    _TEXTURE.fields_by_name['texture']._serialized_options = b'\xa0\xbb\x18\x01'
    _MATERIAL.fields_by_name['material']._options = None
    _MATERIAL.fields_by_name['material']._serialized_options = b'\xa0\xbb\x18\x01'
    _MODELDESC.fields_by_name['mesh']._options = None
    _MODELDESC.fields_by_name['mesh']._serialized_options = b'\xa0\xbb\x18\x01'
    _MODELDESC.fields_by_name['material']._options = None
    _MODELDESC.fields_by_name['material']._serialized_options = b'\xa0\xbb\x18\x01'
    _MODELDESC.fields_by_name['textures']._options = None
    _MODELDESC.fields_by_name['textures']._serialized_options = b'\xa0\xbb\x18\x01'
    _MODELDESC.fields_by_name['skeleton']._options = None
    _MODELDESC.fields_by_name['skeleton']._serialized_options = b'\xa0\xbb\x18\x01'
    _MODELDESC.fields_by_name['animations']._options = None
    _MODELDESC.fields_by_name['animations']._serialized_options = b'\xa0\xbb\x18\x01'
    _MODEL.fields_by_name['rig_scene']._options = None
    _MODEL.fields_by_name['rig_scene']._serialized_options = b'\xa0\xbb\x18\x01'
    _TEXTURE._serialized_start = 114
    _TEXTURE._serialized_end = 163
    _MATERIAL._serialized_start = 166
    _MATERIAL._serialized_end = 302
    _MODELDESC._serialized_start = 305
    _MODELDESC._serialized_end = 547
    _MODEL._serialized_start = 549
    _MODEL._serialized_end = 674
    _RESETCONSTANT._serialized_start = 676
    _RESETCONSTANT._serialized_end = 710
    _SETTEXTURE._serialized_start = 712
    _SETTEXTURE._serialized_end = 768
    _MODELPLAYANIMATION._serialized_start = 771
    _MODELPLAYANIMATION._serialized_end = 903
    _MODELCANCELANIMATION._serialized_start = 905
    _MODELCANCELANIMATION._serialized_end = 927
    _MODELANIMATIONDONE._serialized_start = 929
    _MODELANIMATIONDONE._serialized_end = 989
