# Yaml Syntax

yaml-syntax to check a YAML file with your own standard for keys or fields.

like you want a YAML file with these keys:

```version, service, name```

for this you can make a serializer with pydantic to check it:

```python

from pydantic import BaseModel

class MySyntax(BaseModel):
    version:str
    service:str
    name:str
```

*Note*: You can use any option of BaseModel to build your own serializer. For example, use `Field` to create default values ​​for your fields, or use `typing` to handle required fields, or anything else to make it more advanced.


and for example this is your yaml file:

```yaml
version: 'v1.0.0'
service: 'aws'
name: 'test'
```

then you can check this file is correct or not:

```python
from yaml_syntax.syntax import YamlSyntax

yaml = YamlSyntax.from_file(syntax_schema=MySyntax, yaml_file="test.yaml")
```

now you can use your serialized data:

```python
serialized_data = yaml.serialized_data
print(serialized_data.version)
```

