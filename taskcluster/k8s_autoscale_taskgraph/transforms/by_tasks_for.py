from taskgraph.transforms.base import TransformSequence
from taskgraph.util.schema import resolve_keyed_by

transforms = TransformSequence()


@transforms.add
def evaluate_keyed_by(config, jobs):
    for job in jobs:
        resolve_keyed_by(
            job["worker"]["env"],
            "DRYRUN",
            item_name=job["description"],
            **{"tasks-for": config.params["tasks_for"]},
        )
        resolve_keyed_by(
            job,
            "scopes",
            item_name=job["description"],
            **{"tasks-for": config.params["tasks_for"]},
        )

        yield job
