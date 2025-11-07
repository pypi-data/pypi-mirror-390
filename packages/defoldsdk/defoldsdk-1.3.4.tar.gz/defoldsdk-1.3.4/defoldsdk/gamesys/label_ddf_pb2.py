"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17gamesys/label_ddf.proto\x12\x0fdmGameSystemDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"\xd1\x06\n\tLabelDesc\x12\x1d\n\x04size\x18\x01 \x02(\x0b2\x0f.dmMath.Vector4\x12!\n\x05scale\x18\x02 \x01(\x0b2\x12.dmMath.Vector4One\x12!\n\x05color\x18\x03 \x01(\x0b2\x12.dmMath.Vector4One\x12$\n\x07outline\x18\x04 \x01(\x0b2\x13.dmMath.Vector4WOne\x12#\n\x06shadow\x18\x05 \x01(\x0b2\x13.dmMath.Vector4WOne\x12\x12\n\x07leading\x18\x06 \x01(\x02:\x011\x12\x10\n\x08tracking\x18\x07 \x01(\x02\x12=\n\x05pivot\x18\x08 \x01(\x0e2 .dmGameSystemDDF.LabelDesc.Pivot:\x0cPIVOT_CENTER\x12J\n\nblend_mode\x18\t \x01(\x0e2$.dmGameSystemDDF.LabelDesc.BlendMode:\x10BLEND_MODE_ALPHA\x12\x19\n\nline_break\x18\n \x01(\x08:\x05false\x12\x0c\n\x04text\x18\x0b \x01(\t\x12\x12\n\x04font\x18\x0c \x02(\tB\x04\xa0\xbb\x18\x01\x12\x16\n\x08material\x18\r \x02(\tB\x04\xa0\xbb\x18\x01"\x8f\x01\n\tBlendMode\x12\x1f\n\x10BLEND_MODE_ALPHA\x10\x00\x1a\t\xc2\xc1\x18\x05Alpha\x12\x1b\n\x0eBLEND_MODE_ADD\x10\x01\x1a\x07\xc2\xc1\x18\x03Add\x12!\n\x0fBLEND_MODE_MULT\x10\x03\x1a\x0c\xc2\xc1\x18\x08Multiply\x12!\n\x11BLEND_MODE_SCREEN\x10\x04\x1a\n\xc2\xc1\x18\x06Screen"\xfb\x01\n\x05Pivot\x12\x1c\n\x0cPIVOT_CENTER\x10\x00\x1a\n\xc2\xc1\x18\x06Center\x12\x16\n\x07PIVOT_N\x10\x01\x1a\t\xc2\xc1\x18\x05North\x12\x1c\n\x08PIVOT_NE\x10\x02\x1a\x0e\xc2\xc1\x18\nNorth East\x12\x15\n\x07PIVOT_E\x10\x03\x1a\x08\xc2\xc1\x18\x04East\x12\x1c\n\x08PIVOT_SE\x10\x04\x1a\x0e\xc2\xc1\x18\nSouth East\x12\x16\n\x07PIVOT_S\x10\x05\x1a\t\xc2\xc1\x18\x05South\x12\x1c\n\x08PIVOT_SW\x10\x06\x1a\x0e\xc2\xc1\x18\nSouth West\x12\x15\n\x07PIVOT_W\x10\x07\x1a\x08\xc2\xc1\x18\x04West\x12\x1c\n\x08PIVOT_NW\x10\x08\x1a\x0e\xc2\xc1\x18\nNorth West"\x17\n\x07SetText\x12\x0c\n\x04text\x18\x01 \x02(\tB!\n\x18com.dynamo.gamesys.protoB\x05Label')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gamesys.label_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x18com.dynamo.gamesys.protoB\x05Label'
    _LABELDESC_BLENDMODE.values_by_name['BLEND_MODE_ALPHA']._options = None
    _LABELDESC_BLENDMODE.values_by_name['BLEND_MODE_ALPHA']._serialized_options = b'\xc2\xc1\x18\x05Alpha'
    _LABELDESC_BLENDMODE.values_by_name['BLEND_MODE_ADD']._options = None
    _LABELDESC_BLENDMODE.values_by_name['BLEND_MODE_ADD']._serialized_options = b'\xc2\xc1\x18\x03Add'
    _LABELDESC_BLENDMODE.values_by_name['BLEND_MODE_MULT']._options = None
    _LABELDESC_BLENDMODE.values_by_name['BLEND_MODE_MULT']._serialized_options = b'\xc2\xc1\x18\x08Multiply'
    _LABELDESC_BLENDMODE.values_by_name['BLEND_MODE_SCREEN']._options = None
    _LABELDESC_BLENDMODE.values_by_name['BLEND_MODE_SCREEN']._serialized_options = b'\xc2\xc1\x18\x06Screen'
    _LABELDESC_PIVOT.values_by_name['PIVOT_CENTER']._options = None
    _LABELDESC_PIVOT.values_by_name['PIVOT_CENTER']._serialized_options = b'\xc2\xc1\x18\x06Center'
    _LABELDESC_PIVOT.values_by_name['PIVOT_N']._options = None
    _LABELDESC_PIVOT.values_by_name['PIVOT_N']._serialized_options = b'\xc2\xc1\x18\x05North'
    _LABELDESC_PIVOT.values_by_name['PIVOT_NE']._options = None
    _LABELDESC_PIVOT.values_by_name['PIVOT_NE']._serialized_options = b'\xc2\xc1\x18\nNorth East'
    _LABELDESC_PIVOT.values_by_name['PIVOT_E']._options = None
    _LABELDESC_PIVOT.values_by_name['PIVOT_E']._serialized_options = b'\xc2\xc1\x18\x04East'
    _LABELDESC_PIVOT.values_by_name['PIVOT_SE']._options = None
    _LABELDESC_PIVOT.values_by_name['PIVOT_SE']._serialized_options = b'\xc2\xc1\x18\nSouth East'
    _LABELDESC_PIVOT.values_by_name['PIVOT_S']._options = None
    _LABELDESC_PIVOT.values_by_name['PIVOT_S']._serialized_options = b'\xc2\xc1\x18\x05South'
    _LABELDESC_PIVOT.values_by_name['PIVOT_SW']._options = None
    _LABELDESC_PIVOT.values_by_name['PIVOT_SW']._serialized_options = b'\xc2\xc1\x18\nSouth West'
    _LABELDESC_PIVOT.values_by_name['PIVOT_W']._options = None
    _LABELDESC_PIVOT.values_by_name['PIVOT_W']._serialized_options = b'\xc2\xc1\x18\x04West'
    _LABELDESC_PIVOT.values_by_name['PIVOT_NW']._options = None
    _LABELDESC_PIVOT.values_by_name['PIVOT_NW']._serialized_options = b'\xc2\xc1\x18\nNorth West'
    _LABELDESC.fields_by_name['font']._options = None
    _LABELDESC.fields_by_name['font']._serialized_options = b'\xa0\xbb\x18\x01'
    _LABELDESC.fields_by_name['material']._options = None
    _LABELDESC.fields_by_name['material']._serialized_options = b'\xa0\xbb\x18\x01'
    _LABELDESC._serialized_start = 91
    _LABELDESC._serialized_end = 940
    _LABELDESC_BLENDMODE._serialized_start = 543
    _LABELDESC_BLENDMODE._serialized_end = 686
    _LABELDESC_PIVOT._serialized_start = 689
    _LABELDESC_PIVOT._serialized_end = 940
    _SETTEXT._serialized_start = 942
    _SETTEXT._serialized_end = 965
