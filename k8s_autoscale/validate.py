import jsonschema
import yaml


def validate(config, schema):
    config = yaml.safe_load(config)
    schema = yaml.safe_load(schema)
    jsonschema.validate(config, schema)
