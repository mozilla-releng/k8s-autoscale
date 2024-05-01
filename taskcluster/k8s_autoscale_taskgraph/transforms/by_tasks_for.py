from taskgraph.transforms.base import TransformSequence
from taskgraph.util.schema import resolve_keyed_by

transforms = TransformSequence()


@transforms.add
def evaluate_keyed_by(config, jobs):
    for job in jobs:
        for item in ("worker.env.DRYRUN", "worker.env.DOCKER_TAG", "scopes"):
            resolve_keyed_by(
                job,
                item,
                item_name=job["description"],
                **{"tasks-for": config.params["tasks_for"]},
            )

        yield job
