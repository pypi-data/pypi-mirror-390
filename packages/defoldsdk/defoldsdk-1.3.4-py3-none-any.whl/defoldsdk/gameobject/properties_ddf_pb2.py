"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fgameobject/properties_ddf.proto\x12\x0fdmPropertiesDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"W\n\x18PropertyDeclarationEntry\x12\x0b\n\x03key\x18\x01 \x02(\t\x12\n\n\x02id\x18\x02 \x02(\x04\x12\r\n\x05index\x18\x03 \x02(\r\x12\x13\n\x0belement_ids\x18\x04 \x03(\x04"\xa6\x04\n\x14PropertyDeclarations\x12A\n\x0enumber_entries\x18\x01 \x03(\x0b2).dmPropertiesDDF.PropertyDeclarationEntry\x12?\n\x0chash_entries\x18\x02 \x03(\x0b2).dmPropertiesDDF.PropertyDeclarationEntry\x12>\n\x0burl_entries\x18\x03 \x03(\x0b2).dmPropertiesDDF.PropertyDeclarationEntry\x12B\n\x0fvector3_entries\x18\x04 \x03(\x0b2).dmPropertiesDDF.PropertyDeclarationEntry\x12B\n\x0fvector4_entries\x18\x05 \x03(\x0b2).dmPropertiesDDF.PropertyDeclarationEntry\x12?\n\x0cquat_entries\x18\x06 \x03(\x0b2).dmPropertiesDDF.PropertyDeclarationEntry\x12?\n\x0cbool_entries\x18\x07 \x03(\x0b2).dmPropertiesDDF.PropertyDeclarationEntry\x12\x14\n\x0cfloat_values\x18\x08 \x03(\x02\x12\x13\n\x0bhash_values\x18\t \x03(\x04\x12\x15\n\rstring_values\x18\n \x03(\tB.\n\x1bcom.dynamo.properties.protoB\x0fPropertiesProto')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gameobject.properties_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x1bcom.dynamo.properties.protoB\x0fPropertiesProto'
    _PROPERTYDECLARATIONENTRY._serialized_start = 98
    _PROPERTYDECLARATIONENTRY._serialized_end = 185
    _PROPERTYDECLARATIONS._serialized_start = 188
    _PROPERTYDECLARATIONS._serialized_end = 738
