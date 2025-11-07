"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from defoldsdk.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from defoldsdk.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19gamesys/physics_ddf.proto\x12\x0cdmPhysicsDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"\xc3\x01\n\x0bConvexShape\x122\n\nshape_type\x18\x01 \x02(\x0e2\x1e.dmPhysicsDDF.ConvexShape.Type\x12\x0c\n\x04data\x18\x02 \x03(\x02"r\n\x04Type\x12\x1b\n\x0bTYPE_SPHERE\x10\x00\x1a\n\xc2\xc1\x18\x06Sphere\x12\x15\n\x08TYPE_BOX\x10\x01\x1a\x07\xc2\xc1\x18\x03Box\x12\x1d\n\x0cTYPE_CAPSULE\x10\x02\x1a\x0b\xc2\xc1\x18\x07Capsule\x12\x17\n\tTYPE_HULL\x10\x03\x1a\x08\xc2\xc1\x18\x04Hull"\xde\x02\n\x0eCollisionShape\x122\n\x06shapes\x18\x01 \x03(\x0b2".dmPhysicsDDF.CollisionShape.Shape\x12\x0c\n\x04data\x18\x02 \x03(\x02\x1a\xc1\x01\n\x05Shape\x125\n\nshape_type\x18\x01 \x02(\x0e2!.dmPhysicsDDF.CollisionShape.Type\x12 \n\x08position\x18\x02 \x02(\x0b2\x0e.dmMath.Point3\x12\x1e\n\x08rotation\x18\x03 \x02(\x0b2\x0c.dmMath.Quat\x12\r\n\x05index\x18\x04 \x02(\r\x12\r\n\x05count\x18\x05 \x02(\r\x12\n\n\x02id\x18\x06 \x01(\t\x12\x15\n\x07id_hash\x18\x07 \x01(\x04B\x04\xa8\xbb\x18\x01"F\n\x04Type\x12\x0f\n\x0bTYPE_SPHERE\x10\x00\x12\x0c\n\x08TYPE_BOX\x10\x01\x12\x10\n\x0cTYPE_CAPSULE\x10\x02\x12\r\n\tTYPE_HULL\x10\x03"\xbe\x03\n\x13CollisionObjectDesc\x12\x1d\n\x0fcollision_shape\x18\x01 \x01(\tB\x04\xa0\xbb\x18\x01\x12/\n\x04type\x18\x02 \x02(\x0e2!.dmPhysicsDDF.CollisionObjectType\x12\x0c\n\x04mass\x18\x03 \x02(\x02\x12\x10\n\x08friction\x18\x04 \x02(\x02\x12\x13\n\x0brestitution\x18\x05 \x02(\x02\x12\r\n\x05group\x18\x06 \x02(\t\x12\x0c\n\x04mask\x18\x07 \x03(\t\x12>\n\x18embedded_collision_shape\x18\x08 \x01(\x0b2\x1c.dmPhysicsDDF.CollisionShape\x12\x19\n\x0elinear_damping\x18\t \x01(\x02:\x010\x12\x1a\n\x0fangular_damping\x18\n \x01(\x02:\x010\x12\x1e\n\x0flocked_rotation\x18\x0b \x01(\x08:\x05false\x12\x15\n\x06bullet\x18\x0c \x01(\x08:\x05false\x12\x1d\n\x0fevent_collision\x18\r \x01(\x08:\x04true\x12\x1b\n\revent_contact\x18\x0e \x01(\x08:\x04true\x12\x1b\n\revent_trigger\x18\x0f \x01(\x08:\x04true"N\n\nApplyForce\x12\x1e\n\x05force\x18\x01 \x02(\x0b2\x0f.dmMath.Vector3\x12 \n\x08position\x18\x02 \x02(\x0b2\x0e.dmMath.Point3"\x84\x01\n\x11CollisionResponse\x12\x10\n\x08other_id\x18\x01 \x02(\x04\x12\r\n\x05group\x18\x02 \x02(\x04\x12&\n\x0eother_position\x18\x03 \x02(\x0b2\x0e.dmMath.Point3\x12\x13\n\x0bother_group\x18\x04 \x02(\x04\x12\x11\n\town_group\x18\x05 \x02(\x04"\xd6\x02\n\x14ContactPointResponse\x12 \n\x08position\x18\x01 \x02(\x0b2\x0e.dmMath.Point3\x12\x1f\n\x06normal\x18\x02 \x02(\x0b2\x0f.dmMath.Vector3\x12*\n\x11relative_velocity\x18\x03 \x02(\x0b2\x0f.dmMath.Vector3\x12\x10\n\x08distance\x18\x04 \x02(\x02\x12\x17\n\x0fapplied_impulse\x18\x05 \x02(\x02\x12\x11\n\tlife_time\x18\x06 \x02(\x02\x12\x0c\n\x04mass\x18\x07 \x02(\x02\x12\x12\n\nother_mass\x18\x08 \x02(\x02\x12\x10\n\x08other_id\x18\t \x02(\x04\x12&\n\x0eother_position\x18\n \x02(\x0b2\x0e.dmMath.Point3\x12\r\n\x05group\x18\x0b \x02(\x04\x12\x13\n\x0bother_group\x18\x0c \x02(\x04\x12\x11\n\town_group\x18\r \x02(\x04"i\n\x0fTriggerResponse\x12\x10\n\x08other_id\x18\x01 \x02(\x04\x12\r\n\x05enter\x18\x02 \x02(\x08\x12\r\n\x05group\x18\x03 \x02(\x04\x12\x13\n\x0bother_group\x18\x04 \x02(\x04\x12\x11\n\town_group\x18\x05 \x02(\x04"l\n\x0eRequestRayCast\x12\x1c\n\x04from\x18\x01 \x02(\x0b2\x0e.dmMath.Point3\x12\x1a\n\x02to\x18\x02 \x02(\x0b2\x0e.dmMath.Point3\x12\x0c\n\x04mask\x18\x03 \x02(\r\x12\x12\n\nrequest_id\x18\x04 \x02(\r"\x95\x01\n\x0fRayCastResponse\x12\x10\n\x08fraction\x18\x01 \x02(\x02\x12 \n\x08position\x18\x02 \x02(\x0b2\x0e.dmMath.Point3\x12\x1f\n\x06normal\x18\x03 \x02(\x0b2\x0f.dmMath.Vector3\x12\n\n\x02id\x18\x04 \x02(\x04\x12\r\n\x05group\x18\x05 \x02(\x04\x12\x12\n\nrequest_id\x18\x06 \x02(\r"#\n\rRayCastMissed\x12\x12\n\nrequest_id\x18\x01 \x02(\r"\x11\n\x0fRequestVelocity"g\n\x10VelocityResponse\x12(\n\x0flinear_velocity\x18\x01 \x02(\x0b2\x0f.dmMath.Vector3\x12)\n\x10angular_velocity\x18\x02 \x02(\x0b2\x0f.dmMath.Vector3"\x8e\x01\n\x10SetGridShapeHull\x12\r\n\x05shape\x18\x01 \x02(\r\x12\x0b\n\x03row\x18\x02 \x02(\r\x12\x0e\n\x06column\x18\x03 \x02(\r\x12\x0c\n\x04hull\x18\x04 \x02(\r\x12\x17\n\x0fflip_horizontal\x18\x05 \x02(\r\x12\x15\n\rflip_vertical\x18\x06 \x02(\r\x12\x10\n\x08rotate90\x18\x07 \x02(\r"5\n\x14EnableGridShapeLayer\x12\r\n\x05shape\x18\x01 \x02(\r\x12\x0e\n\x06enable\x18\x02 \x02(\r"\xd1\x01\n\x0cContactPoint\x12 \n\x08position\x18\x01 \x02(\x0b2\x0e.dmMath.Point3\x12)\n\x11instance_position\x18\x02 \x02(\x0b2\x0e.dmMath.Point3\x12\x1f\n\x06normal\x18\x03 \x02(\x0b2\x0f.dmMath.Vector3\x12*\n\x11relative_velocity\x18\x04 \x02(\x0b2\x0f.dmMath.Vector3\x12\x0c\n\x04mass\x18\x05 \x02(\x02\x12\n\n\x02id\x18\x06 \x02(\x04\x12\r\n\x05group\x18\x07 \x02(\x04"\x8c\x01\n\x11ContactPointEvent\x12%\n\x01a\x18\x01 \x02(\x0b2\x1a.dmPhysicsDDF.ContactPoint\x12%\n\x01b\x18\x02 \x02(\x0b2\x1a.dmPhysicsDDF.ContactPoint\x12\x10\n\x08distance\x18\x03 \x02(\x02\x12\x17\n\x0fapplied_impulse\x18\x04 \x02(\x02"H\n\tCollision\x12 \n\x08position\x18\x01 \x02(\x0b2\x0e.dmMath.Point3\x12\n\n\x02id\x18\x02 \x02(\x04\x12\r\n\x05group\x18\x03 \x02(\x04"X\n\x0eCollisionEvent\x12"\n\x01a\x18\x01 \x02(\x0b2\x17.dmPhysicsDDF.Collision\x12"\n\x01b\x18\x02 \x02(\x0b2\x17.dmPhysicsDDF.Collision"$\n\x07Trigger\x12\n\n\x02id\x18\x01 \x02(\x04\x12\r\n\x05group\x18\x02 \x02(\x04"a\n\x0cTriggerEvent\x12\r\n\x05enter\x18\x01 \x02(\x08\x12 \n\x01a\x18\x02 \x02(\x0b2\x15.dmPhysicsDDF.Trigger\x12 \n\x01b\x18\x03 \x02(\x0b2\x15.dmPhysicsDDF.Trigger*\xd7\x01\n\x13CollisionObjectType\x12.\n\x1dCOLLISION_OBJECT_TYPE_DYNAMIC\x10\x00\x1a\x0b\xc2\xc1\x18\x07Dynamic\x122\n\x1fCOLLISION_OBJECT_TYPE_KINEMATIC\x10\x01\x1a\r\xc2\xc1\x18\tKinematic\x12,\n\x1cCOLLISION_OBJECT_TYPE_STATIC\x10\x02\x1a\n\xc2\xc1\x18\x06Static\x12.\n\x1dCOLLISION_OBJECT_TYPE_TRIGGER\x10\x03\x1a\x0b\xc2\xc1\x18\x07TriggerB#\n\x18com.dynamo.gamesys.protoB\x07Physics')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'gamesys.physics_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x18com.dynamo.gamesys.protoB\x07Physics'
    _COLLISIONOBJECTTYPE.values_by_name['COLLISION_OBJECT_TYPE_DYNAMIC']._options = None
    _COLLISIONOBJECTTYPE.values_by_name['COLLISION_OBJECT_TYPE_DYNAMIC']._serialized_options = b'\xc2\xc1\x18\x07Dynamic'
    _COLLISIONOBJECTTYPE.values_by_name['COLLISION_OBJECT_TYPE_KINEMATIC']._options = None
    _COLLISIONOBJECTTYPE.values_by_name['COLLISION_OBJECT_TYPE_KINEMATIC']._serialized_options = b'\xc2\xc1\x18\tKinematic'
    _COLLISIONOBJECTTYPE.values_by_name['COLLISION_OBJECT_TYPE_STATIC']._options = None
    _COLLISIONOBJECTTYPE.values_by_name['COLLISION_OBJECT_TYPE_STATIC']._serialized_options = b'\xc2\xc1\x18\x06Static'
    _COLLISIONOBJECTTYPE.values_by_name['COLLISION_OBJECT_TYPE_TRIGGER']._options = None
    _COLLISIONOBJECTTYPE.values_by_name['COLLISION_OBJECT_TYPE_TRIGGER']._serialized_options = b'\xc2\xc1\x18\x07Trigger'
    _CONVEXSHAPE_TYPE.values_by_name['TYPE_SPHERE']._options = None
    _CONVEXSHAPE_TYPE.values_by_name['TYPE_SPHERE']._serialized_options = b'\xc2\xc1\x18\x06Sphere'
    _CONVEXSHAPE_TYPE.values_by_name['TYPE_BOX']._options = None
    _CONVEXSHAPE_TYPE.values_by_name['TYPE_BOX']._serialized_options = b'\xc2\xc1\x18\x03Box'
    _CONVEXSHAPE_TYPE.values_by_name['TYPE_CAPSULE']._options = None
    _CONVEXSHAPE_TYPE.values_by_name['TYPE_CAPSULE']._serialized_options = b'\xc2\xc1\x18\x07Capsule'
    _CONVEXSHAPE_TYPE.values_by_name['TYPE_HULL']._options = None
    _CONVEXSHAPE_TYPE.values_by_name['TYPE_HULL']._serialized_options = b'\xc2\xc1\x18\x04Hull'
    _COLLISIONSHAPE_SHAPE.fields_by_name['id_hash']._options = None
    _COLLISIONSHAPE_SHAPE.fields_by_name['id_hash']._serialized_options = b'\xa8\xbb\x18\x01'
    _COLLISIONOBJECTDESC.fields_by_name['collision_shape']._options = None
    _COLLISIONOBJECTDESC.fields_by_name['collision_shape']._serialized_options = b'\xa0\xbb\x18\x01'
    _COLLISIONOBJECTTYPE._serialized_start = 3036
    _COLLISIONOBJECTTYPE._serialized_end = 3251
    _CONVEXSHAPE._serialized_start = 90
    _CONVEXSHAPE._serialized_end = 285
    _CONVEXSHAPE_TYPE._serialized_start = 171
    _CONVEXSHAPE_TYPE._serialized_end = 285
    _COLLISIONSHAPE._serialized_start = 288
    _COLLISIONSHAPE._serialized_end = 638
    _COLLISIONSHAPE_SHAPE._serialized_start = 373
    _COLLISIONSHAPE_SHAPE._serialized_end = 566
    _COLLISIONSHAPE_TYPE._serialized_start = 568
    _COLLISIONSHAPE_TYPE._serialized_end = 638
    _COLLISIONOBJECTDESC._serialized_start = 641
    _COLLISIONOBJECTDESC._serialized_end = 1087
    _APPLYFORCE._serialized_start = 1089
    _APPLYFORCE._serialized_end = 1167
    _COLLISIONRESPONSE._serialized_start = 1170
    _COLLISIONRESPONSE._serialized_end = 1302
    _CONTACTPOINTRESPONSE._serialized_start = 1305
    _CONTACTPOINTRESPONSE._serialized_end = 1647
    _TRIGGERRESPONSE._serialized_start = 1649
    _TRIGGERRESPONSE._serialized_end = 1754
    _REQUESTRAYCAST._serialized_start = 1756
    _REQUESTRAYCAST._serialized_end = 1864
    _RAYCASTRESPONSE._serialized_start = 1867
    _RAYCASTRESPONSE._serialized_end = 2016
    _RAYCASTMISSED._serialized_start = 2018
    _RAYCASTMISSED._serialized_end = 2053
    _REQUESTVELOCITY._serialized_start = 2055
    _REQUESTVELOCITY._serialized_end = 2072
    _VELOCITYRESPONSE._serialized_start = 2074
    _VELOCITYRESPONSE._serialized_end = 2177
    _SETGRIDSHAPEHULL._serialized_start = 2180
    _SETGRIDSHAPEHULL._serialized_end = 2322
    _ENABLEGRIDSHAPELAYER._serialized_start = 2324
    _ENABLEGRIDSHAPELAYER._serialized_end = 2377
    _CONTACTPOINT._serialized_start = 2380
    _CONTACTPOINT._serialized_end = 2589
    _CONTACTPOINTEVENT._serialized_start = 2592
    _CONTACTPOINTEVENT._serialized_end = 2732
    _COLLISION._serialized_start = 2734
    _COLLISION._serialized_end = 2806
    _COLLISIONEVENT._serialized_start = 2808
    _COLLISIONEVENT._serialized_end = 2896
    _TRIGGER._serialized_start = 2898
    _TRIGGER._serialized_end = 2934
    _TRIGGEREVENT._serialized_start = 2936
    _TRIGGEREVENT._serialized_end = 3033
