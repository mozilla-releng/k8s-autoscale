import pytest

from k8s_autoscale.slo import get_target_replica_count

args = {"avg_task_duration": 60, "slo_seconds": 300, "capacity_ratio": 1.0}


@pytest.mark.parametrize(
    "pending, running, args, expected",
    [
        (0, 0, args, 0),
        (1, 0, args, 1),
        (100, 0, args, 20),
        (0, 1, args, 0),
        (0, 10, args, 0),
        (0, 100, args, 0),
        (10, 20, args, 20),
        (20, 20, args, 20),
        (80, 20, args, 20),
        (30, 0, args, 6),
        (30, 2, args, 7),
        (30, 5, args, 7),
        (30, 6, args, 8),
        (30, 7, args, 8),
        (30, 8, args, 8),
    ],
)
def test_process(pending, running, args, expected):
    assert get_target_replica_count(pending, running, args) == expected


@pytest.mark.parametrize(
    "pending, running, args, exception_type",
    [(0, 0, {"slo_seconds": 10, "avg_task_duration": 20}, AssertionError)],
)
def test_process_raises(pending, running, args, exception_type):
    with pytest.raises(exception_type):
        get_target_replica_count(pending, running, args)
