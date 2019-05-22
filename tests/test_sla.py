import pytest
from k8s_autoscale.sla import get_new_worker_count

args = {
    "max_replicas": 10,
    "avg_task_duration": 60,
    "sla_seconds": 300,
    "boot_time": 30,
    "capacity_ratio": 1.0,
}
args_capacity = args.copy()
args_capacity["capacity_ratio"] = 0.5


@pytest.mark.parametrize(
    "pending, running, booting, args, expected",
    [
        (0, 0, 0, args, 0),
        (1, 0, 0, args, 1),
        (10000, 0, 0, args, 10),
        (0, 10, 0, args, -10),
        (10, 20, 0, args, 0),
        (30, 0, 0, args, 8),
        (30, 2, 0, args, 6),
        (30, 5, 0, args, 3),
        (30, 6, 0, args, 2),
        (30, 7, 0, args, 1),
        (30, 8, 0, args, 0),
        (30, 8, 2, args, 0),
        (30, 8, 10, args, 0),
        (30, 0, 10, args, 0),
        (30, 5, 10, args, 0),
        (30, 2, 2, args, 4),
        (0, 2, 2, args, -4),
        (0, 0, 2, args, -2),
        (30, 2, 2, args_capacity, 0),
        (30, 2, 0, args_capacity, 2),
        (30, 0, 2, args_capacity, 2),
        (0, 0, 2, args_capacity, -2),
        (0, 4, 2, args_capacity, -6),
    ],
)
def test_process(pending, running, booting, args, expected):
    assert get_new_worker_count(pending, running, booting, args) == expected


@pytest.mark.parametrize(
    "pending, running, booting, args, exception_type",
    [(0, 0, 0, {"sla_seconds": 10, "avg_task_duration": 20}, AssertionError)],
)
def test_process_raises(pending, running, booting, args, exception_type):
    with pytest.raises(exception_type):
        get_new_worker_count(pending, running, booting, args)
