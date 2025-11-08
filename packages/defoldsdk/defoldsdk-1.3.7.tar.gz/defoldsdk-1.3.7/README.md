# defoldsdk
defold protbuff python 

# installling
```bash
pip install defoldsdk
```

# usage : 
all proto objects are under the namespace sdk 
```python
from  defoldsdk import sdk 

for i in sdk : 
    print(i)

x = sdk.Texture()
```
example load collection from string 
```python
from  defoldsdk import sdk 
from google.protobuf.json_format import MessageToJson
from google.protobuf.text_format import MessageToString, Parse

content = '''
name: "menu"
scale_along_z: 0
embedded_instances {
  id: "go"
  data: "components {\\n"
  "  id: \\"menu\\"\\n"
  "  component: \\"/examples/collection/proxy/menu.gui\\"\\n"
  "  position {\\n"
  "    x: 0.0\\n"
  "    y: 0.0\\n"
  "    z: 0.0\\n"
  "  }\\n"
  "  rotation {\\n"
  "    x: 0.0\\n"
  "    y: 0.0\\n"
  "    z: 0.0\\n"
  "    w: 1.0\\n"
  "  }\\n"
  "}\\n"
  ""
  position {
    x: 0.0
    y: 0.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
  scale3 {
    x: 1.0
    y: 1.0
    z: 1.0
  }
}
'''


collection = sdk.CollectionDesc()
Parse(content.encode('utf-8'), collection)
print(MessageToString(collection))
print(MessageToJson(collection,preserving_proto_field_name=True))
```
output : 
```log
name: "menu"
scale_along_z: 0
embedded_instances {
  id: "go"
  data: "components {\n  id: \"menu\"\n  component: \"/examples/collection/proxy/menu.gui\"\n  position {\n    x: 0.0\n    y: 0.0\n    z: 0.0\n  }\n  rotation {\n    x: 0.0\n    y: 0.0\n    z: 0.0\n    w: 1.0\n  }\n}\n"
  position {
    x: 0.0
    y: 0.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
  scale3 {
    x: 1.0
    y: 1.0
    z: 1.0
  }
}

{
  "name": "menu",
  "scale_along_z": 0,
  "embedded_instances": [
    {
      "id": "go",
      "data": "components {\n  id: \"menu\"\n  component: \"/examples/collection/proxy/menu.gui\"\n  position {\n    x: 0.0\n    y: 0.0\n    z: 0.0\n  }\n  rotation {\n    x: 0.0\n    y: 0.0\n    z: 0.0\n    w: 1.0\n  }\n}\n",
      "position": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      },
      "rotation": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "w": 1.0
      },
      "scale3": {
        "x": 1.0,
        "y": 1.0,
        "z": 1.0
      }
    }
  ]
}```






