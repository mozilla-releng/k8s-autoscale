import pytest

from k8s_autoscale.slo import get_new_worker_count

args = {"max_replicas": 10, "avg_task_duration": 60, "slo_seconds": 300, "capacity_ratio": 1.0}
args_capacity = args.copy()
args_capacity["capacity_ratio"] = 0.5


@pytest.mark.parametrize(
    "pending, claimed, running, args, expected",
    [
        (0, 0, 0, args, 0),
        (1, 0, 0, args, 1),
        (10000, 0, 0, args, 10),
        (0, 0, 10, args, -10),
        (10, 0, 20, args, 0),
        (30, 0, 0, args, 6),
        (30, 0, 2, args, 5),
        (30, 0, 5, args, 2),
        (30, 0, 6, args, 2),
        (30, 0, 7, args, 1),
        (30, 0, 8, args, 0),
        (0, 5, 8, args, 0),
    ],
)
def test_process(pending, claimed, running, args, expected):
    assert (
        get_new_worker_count({"pendingTasks": pending, "claimedTasks": claimed}, running, args)
        == expected
    )


@pytest.mark.parametrize(
    "pending, claimed, running, args, exception_type",
    [(0, 0, 0, {"slo_seconds": 10, "avg_task_duration": 20}, AssertionError)],
)
def test_process_raises(pending, claimed, running, args, exception_type):
    with pytest.raises(exception_type):
        get_new_worker_count({"pendingTasks": pending, "claimedTasks": claimed}, running, args)
