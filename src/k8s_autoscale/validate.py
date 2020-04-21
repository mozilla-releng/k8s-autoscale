import jsonschema
import yaml


def validate(config, schema):
    config = yaml.safe_load(config)
    schema = yaml.safe_load(schema)
    jsonschema.validate(config, schema)
    verify_sla_task_duration(config)


def verify_sla_task_duration(config):
    def verify_sla(worker_type):
        if (
            worker_type["autoscale"]["args"]["sla_seconds"]
            < worker_type["autoscale"]["args"]["avg_task_duration"]
        ):
            return f"{worker_type['worker_type']}: sla_seconds shouldn't be less than avg_task_duration"

    errors = list(filter(None, [verify_sla(worker_type) for worker_type in config["worker_types"]]))
    if errors:
        raise ValueError("\n".join(errors))
