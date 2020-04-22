import math


def get_target_replica_count(pending, running, args):
    # TODO: verify all the args
    assert args["slo_seconds"] > args["avg_task_duration"]
    # In case we don't want to cover all the pending tasks
    pending = int(math.ceil(pending * args["capacity_ratio"]))
    # Scale down only when we have no pending tasks
    if pending < 1:
        return 0
    # Assume that all running workers have a task
    outstanding = pending + running
    # How many tasks a replica can process within our tolerance period
    tasks_per_replica = math.floor(args["slo_seconds"] / args["avg_task_duration"])
    # how many tasks can be covered by the running replicas, assuming they are
    # busy and can only take new tasks after they are done with the current one
    # target_replicas = running + new_replicas_needed
    #                 = running + (still_pending / tasks_per_replica)
    #                 = running + ((pending - running_can_cover) / tasks_per_replica
    #                 = running + ((pending - (running*running_tasks_per_replica)) / tasks_per_replica)
    #                 = running + ((pending - (running*(tasks_per_replica-1))) / tasks_per_replica)
    #                 = running + ((pending + running - running*tasks_per_replica) / tasks_per_replica)
    #                 = running + ((pending + running) / tasks_per_replica - running)
    #                 = (pending + running) / tasks_per_replica
    needed_replicas = math.ceil(outstanding / tasks_per_replica)
    # Do not scale down in case we have pending, because some workers will
    # receive SIGUSR1 and won't take any tasks after that.
    needed_replicas = max(needed_replicas, running)

    return needed_replicas
