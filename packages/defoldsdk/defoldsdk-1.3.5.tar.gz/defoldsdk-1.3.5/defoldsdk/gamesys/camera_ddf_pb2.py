"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18gamesys/camera_ddf.proto\x12\x0cdmGamesysDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"\xf8\x01\n\nCameraDesc\x12\x14\n\x0caspect_ratio\x18\x01 \x02(\x02\x12\x0b\n\x03fov\x18\x02 \x02(\x02\x12\x0e\n\x06near_z\x18\x03 \x02(\x02\x12\r\n\x05far_z\x18\x04 \x02(\x02\x12\x1c\n\x11auto_aspect_ratio\x18\x05 \x01(\r:\x010\x12"\n\x17orthographic_projection\x18\x06 \x01(\r:\x010\x12\x1c\n\x11orthographic_zoom\x18\x07 \x01(\x02:\x011\x12H\n\x11orthographic_mode\x18\x08 \x01(\x0e2\x1b.dmGamesysDDF.OrthoZoomMode:\x10ORTHO_MODE_FIXED"\xd9\x01\n\tSetCamera\x12\x14\n\x0caspect_ratio\x18\x01 \x02(\x02\x12\x0b\n\x03fov\x18\x02 \x02(\x02\x12\x0e\n\x06near_z\x18\x03 \x02(\x02\x12\r\n\x05far_z\x18\x04 \x02(\x02\x12"\n\x17orthographic_projection\x18\x05 \x01(\r:\x010\x12\x1c\n\x11orthographic_zoom\x18\x06 \x01(\x02:\x011\x12H\n\x11orthographic_mode\x18\x07 \x01(\x0e2\x1b.dmGamesysDDF.OrthoZoomMode:\x10ORTHO_MODE_FIXED"\x14\n\x12AcquireCameraFocus"\x14\n\x12ReleaseCameraFocus*\x82\x01\n\rOrthoZoomMode\x12\x1f\n\x10ORTHO_MODE_FIXED\x10\x00\x1a\t\xc2\xc1\x18\x05Fixed\x12%\n\x13ORTHO_MODE_AUTO_FIT\x10\x01\x1a\x0c\xc2\xc1\x18\x08Auto Fit\x12)\n\x15ORTHO_MODE_AUTO_COVER\x10\x02\x1a\x0e\xc2\xc1\x18\nAuto CoverB"\n\x18com.dynamo.gamesys.protoB\x06Camera')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gamesys.camera_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x18com.dynamo.gamesys.protoB\x06Camera'
    _ORTHOZOOMMODE.values_by_name['ORTHO_MODE_FIXED']._options = None
    _ORTHOZOOMMODE.values_by_name['ORTHO_MODE_FIXED']._serialized_options = b'\xc2\xc1\x18\x05Fixed'
    _ORTHOZOOMMODE.values_by_name['ORTHO_MODE_AUTO_FIT']._options = None
    _ORTHOZOOMMODE.values_by_name['ORTHO_MODE_AUTO_FIT']._serialized_options = b'\xc2\xc1\x18\x08Auto Fit'
    _ORTHOZOOMMODE.values_by_name['ORTHO_MODE_AUTO_COVER']._options = None
    _ORTHOZOOMMODE.values_by_name['ORTHO_MODE_AUTO_COVER']._serialized_options = b'\xc2\xc1\x18\nAuto Cover'
    _ORTHOZOOMMODE._serialized_start = 604
    _ORTHOZOOMMODE._serialized_end = 734
    _CAMERADESC._serialized_start = 89
    _CAMERADESC._serialized_end = 337
    _SETCAMERA._serialized_start = 340
    _SETCAMERA._serialized_end = 557
    _ACQUIRECAMERAFOCUS._serialized_start = 559
    _ACQUIRECAMERAFOCUS._serialized_end = 579
    _RELEASECAMERAFOCUS._serialized_start = 581
    _RELEASECAMERAFOCUS._serialized_end = 601
