import jsonschema
import yaml


def validate(config, schema):
    config = yaml.safe_load(config)
    schema = yaml.safe_load(schema)
    jsonschema.validate(config, schema)
    verify_slo_task_duration(config)


def verify_slo_task_duration(config):
    def verify_slo(worker_type):
        if (
            worker_type["autoscale"]["args"]["slo_seconds"]
            < worker_type["autoscale"]["args"]["avg_task_duration"]
        ):
            return f"{worker_type['worker_type']}: slo_seconds shouldn't be less than avg_task_duration"

    errors = list(filter(None, [verify_slo(worker_type) for worker_type in config["worker_types"]]))
    if errors:
        raise ValueError("\n".join(errors))
