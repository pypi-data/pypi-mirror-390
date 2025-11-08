"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dresource/liveupdate_ddf.proto\x12\x0fdmLiveUpdateDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"\x1a\n\nHashDigest\x12\x0c\n\x04data\x18\x01 \x02(\x0c"\xb2\x02\n\x0eManifestHeader\x12L\n\x17resource_hash_algorithm\x18\x01 \x02(\x0e2\x1e.dmLiveUpdateDDF.HashAlgorithm:\x0bHASH_SHA256\x12M\n\x18signature_hash_algorithm\x18\x02 \x02(\x0e2\x1e.dmLiveUpdateDDF.HashAlgorithm:\x0bHASH_SHA256\x12J\n\x18signature_sign_algorithm\x18\x03 \x02(\x0e2\x1e.dmLiveUpdateDDF.SignAlgorithm:\x08SIGN_RSA\x127\n\x12project_identifier\x18\x04 \x02(\x0b2\x1b.dmLiveUpdateDDF.HashDigest"\xa6\x01\n\rResourceEntry\x12)\n\x04hash\x18\x01 \x02(\x0b2\x1b.dmLiveUpdateDDF.HashDigest\x12\x0b\n\x03url\x18\x02 \x02(\t\x12\x10\n\x08url_hash\x18\x03 \x02(\x04\x12\x0c\n\x04size\x18\x04 \x02(\r\x12\x17\n\x0fcompressed_size\x18\x05 \x02(\r\x12\x10\n\x05flags\x18\x06 \x02(\r:\x010\x12\x12\n\ndependants\x18\x07 \x03(\x04"\xa8\x01\n\x0cManifestData\x12/\n\x06header\x18\x01 \x02(\x0b2\x1f.dmLiveUpdateDDF.ManifestHeader\x124\n\x0fengine_versions\x18\x02 \x03(\x0b2\x1b.dmLiveUpdateDDF.HashDigest\x121\n\tresources\x18\x03 \x03(\x0b2\x1e.dmLiveUpdateDDF.ResourceEntry"_\n\x0cManifestFile\x12\x0c\n\x04data\x18\x01 \x02(\x0c\x12\x11\n\tsignature\x18\x02 \x02(\x0c\x12\x1a\n\x12archive_identifier\x18\x03 \x01(\x0c\x12\x12\n\x07version\x18\x04 \x02(\r:\x010*`\n\rHashAlgorithm\x12\x10\n\x0cHASH_UNKNOWN\x10\x00\x12\x0c\n\x08HASH_MD5\x10\x01\x12\r\n\tHASH_SHA1\x10\x02\x12\x0f\n\x0bHASH_SHA256\x10\x03\x12\x0f\n\x0bHASH_SHA512\x10\x04*/\n\rSignAlgorithm\x12\x10\n\x0cSIGN_UNKNOWN\x10\x00\x12\x0c\n\x08SIGN_RSA\x10\x01*M\n\x11ResourceEntryFlag\x12\x0b\n\x07BUNDLED\x10\x01\x12\x0c\n\x08EXCLUDED\x10\x02\x12\r\n\tENCRYPTED\x10\x04\x12\x0e\n\nCOMPRESSED\x10\x08B\'\n\x1bcom.dynamo.liveupdate.protoB\x08Manifest')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'resource.liveupdate_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x1bcom.dynamo.liveupdate.protoB\x08Manifest'
    _HASHALGORITHM._serialized_start = 870
    _HASHALGORITHM._serialized_end = 966
    _SIGNALGORITHM._serialized_start = 968
    _SIGNALGORITHM._serialized_end = 1015
    _RESOURCEENTRYFLAG._serialized_start = 1017
    _RESOURCEENTRYFLAG._serialized_end = 1094
    _HASHDIGEST._serialized_start = 96
    _HASHDIGEST._serialized_end = 122
    _MANIFESTHEADER._serialized_start = 125
    _MANIFESTHEADER._serialized_end = 431
    _RESOURCEENTRY._serialized_start = 434
    _RESOURCEENTRY._serialized_end = 600
    _MANIFESTDATA._serialized_start = 603
    _MANIFESTDATA._serialized_end = 771
    _MANIFESTFILE._serialized_start = 773
    _MANIFESTFILE._serialized_end = 868
