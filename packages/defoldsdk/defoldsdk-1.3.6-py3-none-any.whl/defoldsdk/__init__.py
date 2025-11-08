from .render import *
from .script import *
from .engine import *
from .gamesys import *
from .graphics import *
from .ddf import *
from .gameobject import *
from .resource import *

import importlib , pkgutil , collections , os 
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.text_format import  Parse , MessageToString
from google.protobuf.json_format import MessageToDict , MessageToJson , ParseDict

class TypesGenerator : 
    def getDefoldTypes(self) : 
        result = dict()
        pkg_lib = importlib.import_module('defoldsdk')
        for elem in dir(pkg_lib) : 
            may_msg = pkg_lib.__getattribute__(elem)
            if type(may_msg).__name__ == 'MessageMeta' : 
                result[may_msg.__name__] = may_msg
        return collections.namedtuple('defoldsdk' , result.keys() )(**result)
sdk = TypesGenerator().getDefoldTypes()
__all__ = ["sdk"]

