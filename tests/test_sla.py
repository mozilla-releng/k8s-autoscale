import pytest

from k8s_autoscale.sla import get_new_worker_count

args = {"max_replicas": 10, "avg_task_duration": 60, "sla_seconds": 300, "capacity_ratio": 1.0}
args_capacity = args.copy()
args_capacity["capacity_ratio"] = 0.5


@pytest.mark.parametrize(
    "pending, running, args, expected",
    [
        (0, 0, args, 0),
        (1, 0, args, 1),
        (10000, 0, args, 10),
        (0, 10, args, -10),
        (10, 20, args, 0),
        (30, 0, args, 6),
        (30, 2, args, 5),
        (30, 5, args, 2),
        (30, 6, args, 2),
        (30, 7, args, 1),
        (30, 8, args, 0),
    ],
)
def test_process(pending, running, args, expected):
    assert get_new_worker_count(pending, running, args) == expected


@pytest.mark.parametrize(
    "pending, running, args, exception_type",
    [(0, 0, {"sla_seconds": 10, "avg_task_duration": 20}, AssertionError)],
)
def test_process_raises(pending, running, args, exception_type):
    with pytest.raises(exception_type):
        get_new_worker_count(pending, running, args)
