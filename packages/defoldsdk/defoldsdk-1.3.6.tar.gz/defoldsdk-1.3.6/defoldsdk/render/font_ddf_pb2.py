"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15render/font_ddf.proto\x12\x0bdmRenderDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"\x81\x04\n\x08FontDesc\x12\x12\n\x04font\x18\x01 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x16\n\x08material\x18\x02 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x0c\n\x04size\x18\x03 \x02(\r\x12\x14\n\tantialias\x18\x04 \x01(\r:\x011\x12\x10\n\x05alpha\x18\x05 \x01(\x02:\x011\x12\x18\n\routline_alpha\x18\x06 \x01(\x02:\x010\x12\x18\n\routline_width\x18\x07 \x01(\x02:\x010\x12\x17\n\x0cshadow_alpha\x18\x08 \x01(\x02:\x010\x12\x16\n\x0bshadow_blur\x18\t \x01(\r:\x010\x12\x13\n\x08shadow_x\x18\n \x01(\x02:\x010\x12\x13\n\x08shadow_y\x18\x0b \x01(\x02:\x010\x12\x1a\n\x10extra_characters\x18\x0c \x01(\t:\x00\x12B\n\routput_format\x18\r \x01(\x0e2\x1e.dmRenderDDF.FontTextureFormat:\x0bTYPE_BITMAP\x12\x18\n\tall_chars\x18\x0e \x01(\x08:\x05false\x12\x16\n\x0bcache_width\x18\x0f \x01(\r:\x010\x12\x17\n\x0ccache_height\x18\x10 \x01(\r:\x010\x12C\n\x0brender_mode\x18\x11 \x01(\x0e2\x1b.dmRenderDDF.FontRenderMode:\x11MODE_SINGLE_LAYER\x12\x14\n\ncharacters\x18\x12 \x01(\t:\x00"\xaa\x06\n\tGlyphBank\x12,\n\x06glyphs\x18\x01 \x03(\x0b2\x1c.dmRenderDDF.GlyphBank.Glyph\x12\x18\n\rglyph_padding\x18\x02 \x01(\x04:\x010\x12\x19\n\x0eglyph_channels\x18\x03 \x01(\r:\x010\x12\x12\n\nglyph_data\x18\x04 \x01(\x0c\x12\x15\n\nmax_ascent\x18\x05 \x01(\x02:\x010\x12\x16\n\x0bmax_descent\x18\x06 \x01(\x02:\x010\x12\x16\n\x0bmax_advance\x18\x07 \x01(\x02:\x010\x12\x14\n\tmax_width\x18\x08 \x01(\x02:\x010\x12\x15\n\nmax_height\x18\t \x01(\x02:\x010\x12A\n\x0cimage_format\x18\n \x01(\x0e2\x1e.dmRenderDDF.FontTextureFormat:\x0bTYPE_BITMAP\x12\x15\n\nsdf_spread\x18\x0b \x01(\x02:\x011\x12\x16\n\x0bsdf_outline\x18\x0c \x01(\x02:\x010\x12\x15\n\nsdf_shadow\x18\r \x01(\x02:\x010\x12\x16\n\x0bcache_width\x18\x0e \x01(\r:\x010\x12\x17\n\x0ccache_height\x18\x0f \x01(\r:\x010\x12\x1b\n\x10cache_cell_width\x18\x10 \x01(\r:\x010\x12\x1c\n\x11cache_cell_height\x18\x11 \x01(\r:\x010\x12 \n\x15cache_cell_max_ascent\x18\x12 \x01(\r:\x010\x12\x12\n\x07padding\x18\x13 \x01(\r:\x010\x12\x1c\n\ris_monospaced\x18\x14 \x01(\x08:\x05false\x1a\xe8\x01\n\x05Glyph\x12\x11\n\tcharacter\x18\x01 \x02(\r\x12\x10\n\x05width\x18\x02 \x01(\x02:\x010\x12\x16\n\x0bimage_width\x18\x03 \x01(\r:\x010\x12\x12\n\x07advance\x18\x04 \x01(\x02:\x010\x12\x17\n\x0cleft_bearing\x18\x05 \x01(\x02:\x010\x12\x11\n\x06ascent\x18\x06 \x01(\x05:\x010\x12\x12\n\x07descent\x18\x07 \x01(\x05:\x010\x12\x0c\n\x01x\x18\x08 \x01(\x05:\x010\x12\x0c\n\x01y\x18\t \x01(\x05:\x010\x12\x19\n\x11glyph_data_offset\x18\n \x01(\x04\x12\x17\n\x0fglyph_data_size\x18\x0b \x01(\x04"\xf8\x04\n\x07FontMap\x12\x18\n\x08material\x18\x01 \x01(\t:\x00B\x04\xa0\xbb\x18\x01\x12\x1a\n\nglyph_bank\x18\x02 \x01(\t:\x00B\x04\xa0\xbb\x18\x01\x12\x14\n\x04font\x18\x03 \x01(\t:\x00B\x04\xa0\xbb\x18\x01\x12\x0f\n\x04size\x18\x04 \x01(\r:\x010\x12\x14\n\tantialias\x18\x05 \x01(\r:\x011\x12\x13\n\x08shadow_x\x18\x06 \x01(\x02:\x010\x12\x13\n\x08shadow_y\x18\x07 \x01(\x02:\x010\x12\x16\n\x0bshadow_blur\x18\x08 \x01(\r:\x010\x12\x17\n\x0cshadow_alpha\x18\t \x01(\x02:\x011\x12\x10\n\x05alpha\x18\n \x01(\x02:\x011\x12\x18\n\routline_alpha\x18\x0b \x01(\x02:\x011\x12\x18\n\routline_width\x18\x0c \x01(\x02:\x010\x12\x15\n\nlayer_mask\x18\r \x01(\r:\x011\x12B\n\routput_format\x18\x0e \x01(\x0e2\x1e.dmRenderDDF.FontTextureFormat:\x0bTYPE_BITMAP\x12C\n\x0brender_mode\x18\x0f \x01(\x0e2\x1b.dmRenderDDF.FontRenderMode:\x11MODE_SINGLE_LAYER\x12\x18\n\tall_chars\x18\x10 \x01(\x08:\x05false\x12\x14\n\ncharacters\x18\x11 \x01(\t:\x00\x12\x16\n\x0bcache_width\x18\x12 \x01(\r:\x010\x12\x17\n\x0ccache_height\x18\x13 \x01(\r:\x010\x12\x15\n\nsdf_spread\x18\x14 \x01(\x02:\x011\x12\x16\n\x0bsdf_outline\x18\x15 \x01(\x02:\x010\x12\x15\n\nsdf_shadow\x18\x16 \x01(\x02:\x010\x12\x12\n\x07padding\x18\x17 \x01(\r:\x010*]\n\x11FontTextureFormat\x12\x1b\n\x0bTYPE_BITMAP\x10\x00\x1a\n\xc2\xc1\x18\x06Bitmap\x12+\n\x13TYPE_DISTANCE_FIELD\x10\x01\x1a\x12\xc2\xc1\x18\x0eDistance Field*`\n\x0eFontRenderMode\x12\'\n\x11MODE_SINGLE_LAYER\x10\x00\x1a\x10\xc2\xc1\x18\x0cSingle Layer\x12%\n\x10MODE_MULTI_LAYER\x10\x01\x1a\x0f\xc2\xc1\x18\x0bMulti LayerB\x1f\n\x17com.dynamo.render.protoB\x04Font')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'render.font_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x17com.dynamo.render.protoB\x04Font'
    _FONTTEXTUREFORMAT.values_by_name['TYPE_BITMAP']._options = None
    _FONTTEXTUREFORMAT.values_by_name['TYPE_BITMAP']._serialized_options = b'\xc2\xc1\x18\x06Bitmap'
    _FONTTEXTUREFORMAT.values_by_name['TYPE_DISTANCE_FIELD']._options = None
    _FONTTEXTUREFORMAT.values_by_name['TYPE_DISTANCE_FIELD']._serialized_options = b'\xc2\xc1\x18\x0eDistance Field'
    _FONTRENDERMODE.values_by_name['MODE_SINGLE_LAYER']._options = None
    _FONTRENDERMODE.values_by_name['MODE_SINGLE_LAYER']._serialized_options = b'\xc2\xc1\x18\x0cSingle Layer'
    _FONTRENDERMODE.values_by_name['MODE_MULTI_LAYER']._options = None
    _FONTRENDERMODE.values_by_name['MODE_MULTI_LAYER']._serialized_options = b'\xc2\xc1\x18\x0bMulti Layer'
    _FONTDESC.fields_by_name['font']._options = None
    _FONTDESC.fields_by_name['font']._serialized_options = b'\xa0\xbb\x18\x01'
    _FONTDESC.fields_by_name['material']._options = None
    _FONTDESC.fields_by_name['material']._serialized_options = b'\xa0\xbb\x18\x01'
    _FONTMAP.fields_by_name['material']._options = None
    _FONTMAP.fields_by_name['material']._serialized_options = b'\xa0\xbb\x18\x01'
    _FONTMAP.fields_by_name['glyph_bank']._options = None
    _FONTMAP.fields_by_name['glyph_bank']._serialized_options = b'\xa0\xbb\x18\x01'
    _FONTMAP.fields_by_name['font']._options = None
    _FONTMAP.fields_by_name['font']._serialized_options = b'\xa0\xbb\x18\x01'
    _FONTTEXTUREFORMAT._serialized_start = 2048
    _FONTTEXTUREFORMAT._serialized_end = 2141
    _FONTRENDERMODE._serialized_start = 2143
    _FONTRENDERMODE._serialized_end = 2239
    _FONTDESC._serialized_start = 85
    _FONTDESC._serialized_end = 598
    _GLYPHBANK._serialized_start = 601
    _GLYPHBANK._serialized_end = 1411
    _GLYPHBANK_GLYPH._serialized_start = 1179
    _GLYPHBANK_GLYPH._serialized_end = 1411
    _FONTMAP._serialized_start = 1414
    _FONTMAP._serialized_end = 2046
