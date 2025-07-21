import yaml
from cerberus import Validator
from core.tool import Tool


TOOL_SCHEMA = {
    'name': {'type': 'string', 'required': True},
    'command': {'type': 'string', 'required': True},
    'phase': {'type': 'string', 'required': True},
    'output': {'type': 'string', 'required': True},
    'parallel': {'type': 'boolean', 'required': False, 'default': False}
}


def validate_tool_config(tool_dict):
    v = Validator(TOOL_SCHEMA)
    if not v.validate(tool_dict):
        raise ValueError(f"Invalid tool config for {tool_dict.get('name')}: {v.errors}")
    return v.document


def load_tools_from_yaml(path="configs/tools.yaml"):
    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    tool_objs = []
    for td in data['tools']:
        valid_data = validate_tool_config(td)
        tool_objs.append(Tool(**valid_data))

    return tool_objs
