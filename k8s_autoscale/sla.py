import math


def get_new_worker_count(pending, running, booting, args):
    # TODO: verify all the args
    assert args["sla_seconds"] > args["avg_task_duration"]
    # In case we don't want to cover all the pending tasks
    pending = int(math.ceil(pending * args["capacity_ratio"]))
    # Scale down only when we have no pending tasks
    if pending == 0:
        return -(running + booting)
    # How many tasks a replica can process within our tolerance period
    new_tasks_per_replica = math.floor(
        (args["sla_seconds"] - args["boot_time"]) / args["avg_task_duration"]
    )
    # how many tasks can be covered by the running replicas, assuming they are
    # busy and can only take new tasks after they are done with the current one
    running_tasks_per_replica = (
        math.floor(args["sla_seconds"] / args["avg_task_duration"]) - 1
    )
    # how many tasks the booting replicas can cover, assuming they will be
    # available for new jobs as soon as they boot up
    booting_tasks_per_replica = math.floor(
        (args["sla_seconds"] - args["boot_time"]) / args["avg_task_duration"]
    )
    running_can_cover = running * running_tasks_per_replica
    booting_can_cover = booting * booting_tasks_per_replica
    still_pending = pending - (running_can_cover + booting_can_cover)
    if still_pending > 0:
        new_replicas_needed = math.ceil(still_pending / new_tasks_per_replica)
        return min([new_replicas_needed, args["max_replicas"]])
    else:
        return 0
