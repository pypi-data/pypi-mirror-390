"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
from defoldsdk.gameobject import properties_ddf_pb2 as gameobject_dot_properties__ddf__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fgameobject/gameobject_ddf.proto\x12\x0fdmGameObjectDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto\x1a\x1fgameobject/properties_ddf.proto"V\n\x0cPropertyDesc\x12\n\n\x02id\x18\x01 \x02(\t\x12\r\n\x05value\x18\x02 \x02(\t\x12+\n\x04type\x18\x03 \x02(\x0e2\x1d.dmGameObjectDDF.PropertyType"\x91\x02\n\rComponentDesc\x12\n\n\x02id\x18\x01 \x02(\t\x12\x17\n\tcomponent\x18\x02 \x02(\tB\x04\xa0\xbb\x18\x01\x12 \n\x08position\x18\x03 \x01(\x0b2\x0e.dmMath.Point3\x12\x1e\n\x08rotation\x18\x04 \x01(\x0b2\x0c.dmMath.Quat\x121\n\nproperties\x18\x05 \x03(\x0b2\x1d.dmGameObjectDDF.PropertyDesc\x12C\n\x0eproperty_decls\x18\x06 \x01(\x0b2%.dmPropertiesDDF.PropertyDeclarationsB\x04\xa8\xbb\x18\x01\x12!\n\x05scale\x18\x07 \x01(\x0b2\x12.dmMath.Vector3One"\xa4\x01\n\x15EmbeddedComponentDesc\x12\n\n\x02id\x18\x01 \x02(\t\x12\x0c\n\x04type\x18\x02 \x02(\t\x12\x0c\n\x04data\x18\x03 \x02(\t\x12 \n\x08position\x18\x04 \x01(\x0b2\x0e.dmMath.Point3\x12\x1e\n\x08rotation\x18\x05 \x01(\x0b2\x0c.dmMath.Quat\x12!\n\x05scale\x18\x06 \x01(\x0b2\x12.dmMath.Vector3One"\xae\x01\n\rPrototypeDesc\x122\n\ncomponents\x18\x01 \x03(\x0b2\x1e.dmGameObjectDDF.ComponentDesc\x12C\n\x13embedded_components\x18\x02 \x03(\x0b2&.dmGameObjectDDF.EmbeddedComponentDesc\x12$\n\x12property_resources\x18\x03 \x03(\tB\x08\xa8\xbb\x18\x01\xa0\xbb\x18\x01"\x9b\x01\n\x15ComponentPropertyDesc\x12\n\n\x02id\x18\x01 \x02(\t\x121\n\nproperties\x18\x02 \x03(\x0b2\x1d.dmGameObjectDDF.PropertyDesc\x12C\n\x0eproperty_decls\x18\x03 \x01(\x0b2%.dmPropertiesDDF.PropertyDeclarationsB\x04\xa8\xbb\x18\x01"8\n\x10ComponenTypeDesc\x12\x11\n\tname_hash\x18\x01 \x02(\x04\x12\x11\n\tmax_count\x18\x02 \x02(\r"\x83\x02\n\x0cInstanceDesc\x12\n\n\x02id\x18\x01 \x02(\t\x12\x17\n\tprototype\x18\x02 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x10\n\x08children\x18\x03 \x03(\t\x12 \n\x08position\x18\x04 \x01(\x0b2\x0e.dmMath.Point3\x12\x1e\n\x08rotation\x18\x05 \x01(\x0b2\x0c.dmMath.Quat\x12D\n\x14component_properties\x18\x06 \x03(\x0b2&.dmGameObjectDDF.ComponentPropertyDesc\x12\x10\n\x05scale\x18\x07 \x01(\x02:\x011\x12"\n\x06scale3\x18\x08 \x01(\x0b2\x12.dmMath.Vector3One"\x80\x02\n\x14EmbeddedInstanceDesc\x12\n\n\x02id\x18\x01 \x02(\t\x12\x10\n\x08children\x18\x02 \x03(\t\x12\x0c\n\x04data\x18\x03 \x02(\t\x12 \n\x08position\x18\x04 \x01(\x0b2\x0e.dmMath.Point3\x12\x1e\n\x08rotation\x18\x05 \x01(\x0b2\x0c.dmMath.Quat\x12D\n\x14component_properties\x18\x06 \x03(\x0b2&.dmGameObjectDDF.ComponentPropertyDesc\x12\x10\n\x05scale\x18\x07 \x01(\x02:\x011\x12"\n\x06scale3\x18\x08 \x01(\x0b2\x12.dmMath.Vector3One"^\n\x14InstancePropertyDesc\x12\n\n\x02id\x18\x01 \x02(\t\x12:\n\nproperties\x18\x02 \x03(\x0b2&.dmGameObjectDDF.ComponentPropertyDesc"\xfa\x01\n\x16CollectionInstanceDesc\x12\n\n\x02id\x18\x01 \x02(\t\x12\x18\n\ncollection\x18\x02 \x02(\tB\x04\xa0\xbb\x18\x01\x12 \n\x08position\x18\x03 \x01(\x0b2\x0e.dmMath.Point3\x12\x1e\n\x08rotation\x18\x04 \x01(\x0b2\x0c.dmMath.Quat\x12\x10\n\x05scale\x18\x05 \x01(\x02:\x011\x12"\n\x06scale3\x18\x07 \x01(\x0b2\x12.dmMath.Vector3One\x12B\n\x13instance_properties\x18\x06 \x03(\x0b2%.dmGameObjectDDF.InstancePropertyDesc"\xdc\x02\n\x0eCollectionDesc\x12\x0c\n\x04name\x18\x01 \x02(\t\x120\n\tinstances\x18\x02 \x03(\x0b2\x1d.dmGameObjectDDF.InstanceDesc\x12E\n\x14collection_instances\x18\x03 \x03(\x0b2\'.dmGameObjectDDF.CollectionInstanceDesc\x12\x18\n\rscale_along_z\x18\x04 \x01(\r:\x010\x12A\n\x12embedded_instances\x18\x05 \x03(\x0b2%.dmGameObjectDDF.EmbeddedInstanceDesc\x12$\n\x12property_resources\x18\x06 \x03(\tB\x08\xa8\xbb\x18\x01\xa0\xbb\x18\x01\x12@\n\x0fcomponent_types\x18\x07 \x03(\x0b2!.dmGameObjectDDF.ComponenTypeDescB\x04\xa8\xbb\x18\x01"\x13\n\x11AcquireInputFocus"\x13\n\x11ReleaseInputFocus"B\n\tSetParent\x12\x14\n\tparent_id\x18\x01 \x01(\x04:\x010\x12\x1f\n\x14keep_world_transform\x18\x02 \x01(\r:\x011"\x08\n\x06Enable"\t\n\x07Disable"h\n\rScriptMessage\x12\x17\n\x0fdescriptor_hash\x18\x01 \x02(\x04\x12\x14\n\x0cpayload_size\x18\x02 \x02(\r\x12\x10\n\x08function\x18\x03 \x01(\r\x12\x16\n\x0eunref_function\x18\x04 \x01(\x08"\'\n\x12ScriptUnrefMessage\x12\x11\n\treference\x18\x01 \x02(\r*\xf4\x01\n\x0cPropertyType\x12\x18\n\x14PROPERTY_TYPE_NUMBER\x10\x00\x12\x16\n\x12PROPERTY_TYPE_HASH\x10\x01\x12\x15\n\x11PROPERTY_TYPE_URL\x10\x02\x12\x19\n\x15PROPERTY_TYPE_VECTOR3\x10\x03\x12\x19\n\x15PROPERTY_TYPE_VECTOR4\x10\x04\x12\x16\n\x12PROPERTY_TYPE_QUAT\x10\x05\x12\x19\n\x15PROPERTY_TYPE_BOOLEAN\x10\x06\x12\x19\n\x15PROPERTY_TYPE_MATRIX4\x10\x07\x12\x17\n\x13PROPERTY_TYPE_COUNT\x10\x08B)\n\x1bcom.dynamo.gameobject.protoB\nGameObject')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gameobject.gameobject_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x1bcom.dynamo.gameobject.protoB\nGameObject'
    _COMPONENTDESC.fields_by_name['component']._options = None
    _COMPONENTDESC.fields_by_name['component']._serialized_options = b'\xa0\xbb\x18\x01'
    _COMPONENTDESC.fields_by_name['property_decls']._options = None
    _COMPONENTDESC.fields_by_name['property_decls']._serialized_options = b'\xa8\xbb\x18\x01'
    _PROTOTYPEDESC.fields_by_name['property_resources']._options = None
    _PROTOTYPEDESC.fields_by_name['property_resources']._serialized_options = b'\xa8\xbb\x18\x01\xa0\xbb\x18\x01'
    _COMPONENTPROPERTYDESC.fields_by_name['property_decls']._options = None
    _COMPONENTPROPERTYDESC.fields_by_name['property_decls']._serialized_options = b'\xa8\xbb\x18\x01'
    _INSTANCEDESC.fields_by_name['prototype']._options = None
    _INSTANCEDESC.fields_by_name['prototype']._serialized_options = b'\xa0\xbb\x18\x01'
    _COLLECTIONINSTANCEDESC.fields_by_name['collection']._options = None
    _COLLECTIONINSTANCEDESC.fields_by_name['collection']._serialized_options = b'\xa0\xbb\x18\x01'
    _COLLECTIONDESC.fields_by_name['property_resources']._options = None
    _COLLECTIONDESC.fields_by_name['property_resources']._serialized_options = b'\xa8\xbb\x18\x01\xa0\xbb\x18\x01'
    _COLLECTIONDESC.fields_by_name['component_types']._options = None
    _COLLECTIONDESC.fields_by_name['component_types']._serialized_options = b'\xa8\xbb\x18\x01'
    _PROPERTYTYPE._serialized_start = 2555
    _PROPERTYTYPE._serialized_end = 2799
    _PROPERTYDESC._serialized_start = 131
    _PROPERTYDESC._serialized_end = 217
    _COMPONENTDESC._serialized_start = 220
    _COMPONENTDESC._serialized_end = 493
    _EMBEDDEDCOMPONENTDESC._serialized_start = 496
    _EMBEDDEDCOMPONENTDESC._serialized_end = 660
    _PROTOTYPEDESC._serialized_start = 663
    _PROTOTYPEDESC._serialized_end = 837
    _COMPONENTPROPERTYDESC._serialized_start = 840
    _COMPONENTPROPERTYDESC._serialized_end = 995
    _COMPONENTYPEDESC._serialized_start = 997
    _COMPONENTYPEDESC._serialized_end = 1053
    _INSTANCEDESC._serialized_start = 1056
    _INSTANCEDESC._serialized_end = 1315
    _EMBEDDEDINSTANCEDESC._serialized_start = 1318
    _EMBEDDEDINSTANCEDESC._serialized_end = 1574
    _INSTANCEPROPERTYDESC._serialized_start = 1576
    _INSTANCEPROPERTYDESC._serialized_end = 1670
    _COLLECTIONINSTANCEDESC._serialized_start = 1673
    _COLLECTIONINSTANCEDESC._serialized_end = 1923
    _COLLECTIONDESC._serialized_start = 1926
    _COLLECTIONDESC._serialized_end = 2274
    _ACQUIREINPUTFOCUS._serialized_start = 2276
    _ACQUIREINPUTFOCUS._serialized_end = 2295
    _RELEASEINPUTFOCUS._serialized_start = 2297
    _RELEASEINPUTFOCUS._serialized_end = 2316
    _SETPARENT._serialized_start = 2318
    _SETPARENT._serialized_end = 2384
    _ENABLE._serialized_start = 2386
    _ENABLE._serialized_end = 2394
    _DISABLE._serialized_start = 2396
    _DISABLE._serialized_end = 2405
    _SCRIPTMESSAGE._serialized_start = 2407
    _SCRIPTMESSAGE._serialized_end = 2511
    _SCRIPTUNREFMESSAGE._serialized_start = 2513
    _SCRIPTUNREFMESSAGE._serialized_end = 2552
