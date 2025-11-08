"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17render/render_ddf.proto\x12\x0bdmRenderDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"\xaa\x02\n\x13RenderPrototypeDesc\x12\x14\n\x06script\x18\x01 \x02(\tB\x04\xa0\xbb\x18\x01\x12@\n\tmaterials\x18\x02 \x03(\x0b2-.dmRenderDDF.RenderPrototypeDesc.MaterialDesc\x12M\n\x10render_resources\x18\x03 \x03(\x0b23.dmRenderDDF.RenderPrototypeDesc.RenderResourceDesc\x1a4\n\x0cMaterialDesc\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x16\n\x08material\x18\x02 \x02(\tB\x04\xa0\xbb\x18\x01\x1a6\n\x12RenderResourceDesc\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x12\n\x04path\x18\x02 \x02(\tB\x04\xa0\xbb\x18\x01":\n\x08DrawText\x12 \n\x08position\x18\x01 \x02(\x0b2\x0e.dmMath.Point3\x12\x0c\n\x04text\x18\x02 \x02(\t"_\n\rDrawDebugText\x12 \n\x08position\x18\x01 \x02(\x0b2\x0e.dmMath.Point3\x12\x0c\n\x04text\x18\x02 \x02(\t\x12\x1e\n\x05color\x18\x03 \x02(\x0b2\x0f.dmMath.Vector4"r\n\x08DrawLine\x12#\n\x0bstart_point\x18\x01 \x02(\x0b2\x0e.dmMath.Point3\x12!\n\tend_point\x18\x02 \x02(\x0b2\x0e.dmMath.Point3\x12\x1e\n\x05color\x18\x03 \x02(\x0b2\x0f.dmMath.Vector4".\n\rWindowResized\x12\r\n\x05width\x18\x01 \x02(\r\x12\x0e\n\x06height\x18\x02 \x02(\r"\'\n\x06Resize\x12\r\n\x05width\x18\x01 \x02(\r\x12\x0e\n\x06height\x18\x02 \x02(\r",\n\nClearColor\x12\x1e\n\x05color\x18\x01 \x02(\x0b2\x0f.dmMath.Vector4"O\n\x17DisplayProfileQualifier\x12\r\n\x05width\x18\x01 \x02(\r\x12\x0e\n\x06height\x18\x02 \x02(\r\x12\x15\n\rdevice_models\x18\x03 \x03(\t"X\n\x0eDisplayProfile\x12\x0c\n\x04name\x18\x01 \x02(\t\x128\n\nqualifiers\x18\x02 \x03(\x0b2$.dmRenderDDF.DisplayProfileQualifier"e\n\x0fDisplayProfiles\x12-\n\x08profiles\x18\x01 \x03(\x0b2\x1b.dmRenderDDF.DisplayProfile\x12#\n\x15auto_layout_selection\x18\x02 \x01(\x08:\x04trueB!\n\x17com.dynamo.render.protoB\x06Render')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'render.render_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x17com.dynamo.render.protoB\x06Render'
    _RENDERPROTOTYPEDESC_MATERIALDESC.fields_by_name['material']._options = None
    _RENDERPROTOTYPEDESC_MATERIALDESC.fields_by_name['material']._serialized_options = b'\xa0\xbb\x18\x01'
    _RENDERPROTOTYPEDESC_RENDERRESOURCEDESC.fields_by_name['path']._options = None
    _RENDERPROTOTYPEDESC_RENDERRESOURCEDESC.fields_by_name['path']._serialized_options = b'\xa0\xbb\x18\x01'
    _RENDERPROTOTYPEDESC.fields_by_name['script']._options = None
    _RENDERPROTOTYPEDESC.fields_by_name['script']._serialized_options = b'\xa0\xbb\x18\x01'
    _RENDERPROTOTYPEDESC._serialized_start = 87
    _RENDERPROTOTYPEDESC._serialized_end = 385
    _RENDERPROTOTYPEDESC_MATERIALDESC._serialized_start = 277
    _RENDERPROTOTYPEDESC_MATERIALDESC._serialized_end = 329
    _RENDERPROTOTYPEDESC_RENDERRESOURCEDESC._serialized_start = 331
    _RENDERPROTOTYPEDESC_RENDERRESOURCEDESC._serialized_end = 385
    _DRAWTEXT._serialized_start = 387
    _DRAWTEXT._serialized_end = 445
    _DRAWDEBUGTEXT._serialized_start = 447
    _DRAWDEBUGTEXT._serialized_end = 542
    _DRAWLINE._serialized_start = 544
    _DRAWLINE._serialized_end = 658
    _WINDOWRESIZED._serialized_start = 660
    _WINDOWRESIZED._serialized_end = 706
    _RESIZE._serialized_start = 708
    _RESIZE._serialized_end = 747
    _CLEARCOLOR._serialized_start = 749
    _CLEARCOLOR._serialized_end = 793
    _DISPLAYPROFILEQUALIFIER._serialized_start = 795
    _DISPLAYPROFILEQUALIFIER._serialized_end = 874
    _DISPLAYPROFILE._serialized_start = 876
    _DISPLAYPROFILE._serialized_end = 964
    _DISPLAYPROFILES._serialized_start = 966
    _DISPLAYPROFILES._serialized_end = 1067
