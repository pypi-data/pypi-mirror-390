"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
from defoldsdk.graphics import graphics_ddf_pb2 as graphics_dot_graphics__ddf__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19render/material_ddf.proto\x12\x0bdmRenderDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto\x1a\x1bgraphics/graphics_ddf.proto"\xd1\x10\n\x0cMaterialDesc\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x0c\n\x04tags\x18\x02 \x03(\t\x12\x1c\n\x0evertex_program\x18\x03 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x1e\n\x10fragment_program\x18\x04 \x02(\tB\x04\xa0\xbb\x18\x01\x12;\n\x0cvertex_space\x18\x05 \x01(\x0e2%.dmRenderDDF.MaterialDesc.VertexSpace\x12<\n\x10vertex_constants\x18\x06 \x03(\x0b2".dmRenderDDF.MaterialDesc.Constant\x12>\n\x12fragment_constants\x18\x07 \x03(\x0b2".dmRenderDDF.MaterialDesc.Constant\x12\x10\n\x08textures\x18\x08 \x03(\t\x123\n\x08samplers\x18\t \x03(\x0b2!.dmRenderDDF.MaterialDesc.Sampler\x12\x19\n\x0emax_page_count\x18\n \x01(\r:\x010\x12/\n\nattributes\x18\x0b \x03(\x0b2\x1b.dmGraphics.VertexAttribute\x12\x19\n\x07program\x18\x0c \x01(\tB\x08\xa0\xbb\x18\x01\xa8\xbb\x18\x01\x12E\n\x0epbr_parameters\x18\r \x01(\x0b2\'.dmRenderDDF.MaterialDesc.PbrParametersB\x04\xa8\xbb\x18\x01\x1an\n\x08Constant\x12\x0c\n\x04name\x18\x01 \x02(\t\x124\n\x04type\x18\x02 \x02(\x0e2&.dmRenderDDF.MaterialDesc.ConstantType\x12\x1e\n\x05value\x18\x03 \x03(\x0b2\x0f.dmMath.Vector4\x1a\x9f\x02\n\rPbrParameters\x12\x16\n\x0ehas_parameters\x18\x01 \x01(\x08\x12\x1e\n\x16has_metallic_roughness\x18\x02 \x01(\x08\x12\x1f\n\x17has_specular_glossiness\x18\x03 \x01(\x08\x12\x15\n\rhas_clearcoat\x18\x04 \x01(\x08\x12\x18\n\x10has_transmission\x18\x05 \x01(\x08\x12\x0f\n\x07has_ior\x18\x06 \x01(\x08\x12\x14\n\x0chas_specular\x18\x07 \x01(\x08\x12\x12\n\nhas_volume\x18\x08 \x01(\x08\x12\x11\n\thas_sheen\x18\t \x01(\x08\x12\x1d\n\x15has_emissive_strength\x18\n \x01(\x08\x12\x17\n\x0fhas_iridescence\x18\x0b \x01(\x08\x1a\xe5\x02\n\x07Sampler\x12\x0c\n\x04name\x18\x01 \x02(\t\x122\n\x06wrap_u\x18\x02 \x02(\x0e2".dmRenderDDF.MaterialDesc.WrapMode\x122\n\x06wrap_v\x18\x03 \x02(\x0e2".dmRenderDDF.MaterialDesc.WrapMode\x12;\n\nfilter_min\x18\x04 \x02(\x0e2\'.dmRenderDDF.MaterialDesc.FilterModeMin\x12;\n\nfilter_mag\x18\x05 \x02(\x0e2\'.dmRenderDDF.MaterialDesc.FilterModeMag\x12\x19\n\x0emax_anisotropy\x18\x06 \x01(\x02:\x011\x12\x1f\n\x11name_indirections\x18\x07 \x03(\x04B\x04\xa8\xbb\x18\x01\x12\x15\n\x07texture\x18\x08 \x01(\tB\x04\xa0\xbb\x18\x01\x12\x17\n\tname_hash\x18\t \x01(\x04B\x04\xa8\xbb\x18\x01"\xa4\x02\n\x0cConstantType\x12\x16\n\x12CONSTANT_TYPE_USER\x10\x00\x12\x1a\n\x16CONSTANT_TYPE_VIEWPROJ\x10\x01\x12\x17\n\x13CONSTANT_TYPE_WORLD\x10\x02\x12\x19\n\x15CONSTANT_TYPE_TEXTURE\x10\x03\x12\x16\n\x12CONSTANT_TYPE_VIEW\x10\x04\x12\x1c\n\x18CONSTANT_TYPE_PROJECTION\x10\x05\x12\x18\n\x14CONSTANT_TYPE_NORMAL\x10\x06\x12\x1b\n\x17CONSTANT_TYPE_WORLDVIEW\x10\x07\x12\x1f\n\x1bCONSTANT_TYPE_WORLDVIEWPROJ\x10\x08\x12\x1e\n\x1aCONSTANT_TYPE_USER_MATRIX4\x10\t"=\n\x0bVertexSpace\x12\x16\n\x12VERTEX_SPACE_WORLD\x10\x00\x12\x16\n\x12VERTEX_SPACE_LOCAL\x10\x01"\\\n\x08WrapMode\x12\x14\n\x10WRAP_MODE_REPEAT\x10\x00\x12\x1d\n\x19WRAP_MODE_MIRRORED_REPEAT\x10\x01\x12\x1b\n\x17WRAP_MODE_CLAMP_TO_EDGE\x10\x02"\x91\x02\n\rFilterModeMin\x12\x1b\n\x17FILTER_MODE_MIN_NEAREST\x10\x00\x12\x1a\n\x16FILTER_MODE_MIN_LINEAR\x10\x01\x12*\n&FILTER_MODE_MIN_NEAREST_MIPMAP_NEAREST\x10\x02\x12)\n%FILTER_MODE_MIN_NEAREST_MIPMAP_LINEAR\x10\x03\x12)\n%FILTER_MODE_MIN_LINEAR_MIPMAP_NEAREST\x10\x04\x12(\n$FILTER_MODE_MIN_LINEAR_MIPMAP_LINEAR\x10\x05\x12\x1b\n\x17FILTER_MODE_MIN_DEFAULT\x10\x06"e\n\rFilterModeMag\x12\x1b\n\x17FILTER_MODE_MAG_NEAREST\x10\x00\x12\x1a\n\x16FILTER_MODE_MAG_LINEAR\x10\x01\x12\x1b\n\x17FILTER_MODE_MAG_DEFAULT\x10\x02B#\n\x17com.dynamo.render.protoB\x08Material')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'render.material_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x17com.dynamo.render.protoB\x08Material'
    _MATERIALDESC_SAMPLER.fields_by_name['name_indirections']._options = None
    _MATERIALDESC_SAMPLER.fields_by_name['name_indirections']._serialized_options = b'\xa8\xbb\x18\x01'
    _MATERIALDESC_SAMPLER.fields_by_name['texture']._options = None
    _MATERIALDESC_SAMPLER.fields_by_name['texture']._serialized_options = b'\xa0\xbb\x18\x01'
    _MATERIALDESC_SAMPLER.fields_by_name['name_hash']._options = None
    _MATERIALDESC_SAMPLER.fields_by_name['name_hash']._serialized_options = b'\xa8\xbb\x18\x01'
    _MATERIALDESC.fields_by_name['vertex_program']._options = None
    _MATERIALDESC.fields_by_name['vertex_program']._serialized_options = b'\xa0\xbb\x18\x01'
    _MATERIALDESC.fields_by_name['fragment_program']._options = None
    _MATERIALDESC.fields_by_name['fragment_program']._serialized_options = b'\xa0\xbb\x18\x01'
    _MATERIALDESC.fields_by_name['program']._options = None
    _MATERIALDESC.fields_by_name['program']._serialized_options = b'\xa0\xbb\x18\x01\xa8\xbb\x18\x01'
    _MATERIALDESC.fields_by_name['pbr_parameters']._options = None
    _MATERIALDESC.fields_by_name['pbr_parameters']._serialized_options = b'\xa8\xbb\x18\x01'
    _MATERIALDESC._serialized_start = 118
    _MATERIALDESC._serialized_end = 2247
    _MATERIALDESC_CONSTANT._serialized_start = 656
    _MATERIALDESC_CONSTANT._serialized_end = 766
    _MATERIALDESC_PBRPARAMETERS._serialized_start = 769
    _MATERIALDESC_PBRPARAMETERS._serialized_end = 1056
    _MATERIALDESC_SAMPLER._serialized_start = 1059
    _MATERIALDESC_SAMPLER._serialized_end = 1416
    _MATERIALDESC_CONSTANTTYPE._serialized_start = 1419
    _MATERIALDESC_CONSTANTTYPE._serialized_end = 1711
    _MATERIALDESC_VERTEXSPACE._serialized_start = 1713
    _MATERIALDESC_VERTEXSPACE._serialized_end = 1774
    _MATERIALDESC_WRAPMODE._serialized_start = 1776
    _MATERIALDESC_WRAPMODE._serialized_end = 1868
    _MATERIALDESC_FILTERMODEMIN._serialized_start = 1871
    _MATERIALDESC_FILTERMODEMIN._serialized_end = 2144
    _MATERIALDESC_FILTERMODEMAG._serialized_start = 2146
    _MATERIALDESC_FILTERMODEMAG._serialized_end = 2247
