"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16gamesys/mesh_ddf.proto\x12\tdmMeshDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"\xde\x02\n\x08MeshDesc\x12\x16\n\x08material\x18\x01 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x16\n\x08vertices\x18\x02 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x16\n\x08textures\x18\x03 \x03(\tB\x04\xa0\xbb\x18\x01\x12N\n\x0eprimitive_type\x18\x04 \x01(\x0e2!.dmMeshDDF.MeshDesc.PrimitiveType:\x13PRIMITIVE_TRIANGLES\x12\x17\n\x0fposition_stream\x18\x05 \x01(\t\x12\x15\n\rnormal_stream\x18\x06 \x01(\t"\x89\x01\n\rPrimitiveType\x12\x1e\n\x0fPRIMITIVE_LINES\x10\x01\x1a\t\xc2\xc1\x18\x05Lines\x12&\n\x13PRIMITIVE_TRIANGLES\x10\x04\x1a\r\xc2\xc1\x18\tTriangles\x120\n\x18PRIMITIVE_TRIANGLE_STRIP\x10\x05\x1a\x12\xc2\xc1\x18\x0eTriangle StripB%\n\x18com.dynamo.gamesys.protoB\tMeshProto')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gamesys.mesh_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x18com.dynamo.gamesys.protoB\tMeshProto'
    _MESHDESC_PRIMITIVETYPE.values_by_name['PRIMITIVE_LINES']._options = None
    _MESHDESC_PRIMITIVETYPE.values_by_name['PRIMITIVE_LINES']._serialized_options = b'\xc2\xc1\x18\x05Lines'
    _MESHDESC_PRIMITIVETYPE.values_by_name['PRIMITIVE_TRIANGLES']._options = None
    _MESHDESC_PRIMITIVETYPE.values_by_name['PRIMITIVE_TRIANGLES']._serialized_options = b'\xc2\xc1\x18\tTriangles'
    _MESHDESC_PRIMITIVETYPE.values_by_name['PRIMITIVE_TRIANGLE_STRIP']._options = None
    _MESHDESC_PRIMITIVETYPE.values_by_name['PRIMITIVE_TRIANGLE_STRIP']._serialized_options = b'\xc2\xc1\x18\x0eTriangle Strip'
    _MESHDESC.fields_by_name['material']._options = None
    _MESHDESC.fields_by_name['material']._serialized_options = b'\xa0\xbb\x18\x01'
    _MESHDESC.fields_by_name['vertices']._options = None
    _MESHDESC.fields_by_name['vertices']._serialized_options = b'\xa0\xbb\x18\x01'
    _MESHDESC.fields_by_name['textures']._options = None
    _MESHDESC.fields_by_name['textures']._serialized_options = b'\xa0\xbb\x18\x01'
    _MESHDESC._serialized_start = 84
    _MESHDESC._serialized_end = 434
    _MESHDESC_PRIMITIVETYPE._serialized_start = 297
    _MESHDESC_PRIMITIVETYPE._serialized_end = 434
