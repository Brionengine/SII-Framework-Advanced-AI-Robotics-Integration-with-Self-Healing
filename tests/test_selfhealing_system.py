"""
Tests for the self-healing system's snapshot and rollback behaviour.

"Roll back to the last known good state" is only meaningful if the target is
actually good and survives being used, so those are the properties asserted
throughout.
"""

import pytest

from selfhealing_system import SelfHealingSystem


@pytest.fixture
def system():
    s = SelfHealingSystem(components=['CPU', 'Memory'])
    s.performance_metrics = {'CPU': 30.0, 'Memory': 40.0}
    return s


def make_unhealthy(system):
    system.performance_metrics['CPU'] = 150.0


# -- Rollback targets a healthy state ---------------------------------------


def test_rollback_restores_the_healthy_state(system):
    system.take_snapshot()          # healthy
    make_unhealthy(system)

    assert system.rollback() is True
    assert system.performance_metrics['CPU'] == 30.0


def test_rollback_skips_unhealthy_snapshots(system):
    """Regression: rollback used to restore the newest snapshot, good or not."""
    system.take_snapshot()          # healthy, CPU=30
    make_unhealthy(system)
    system.take_snapshot()          # unhealthy, CPU=150

    system.rollback()

    assert system.performance_metrics['CPU'] == 30.0


def test_rollback_picks_the_most_recent_healthy_snapshot(system):
    system.take_snapshot()                       # CPU=30
    system.performance_metrics['CPU'] = 45.0
    system.take_snapshot()                       # CPU=45, still healthy
    make_unhealthy(system)

    system.rollback()

    assert system.performance_metrics['CPU'] == 45.0


def test_rollback_fails_when_no_healthy_snapshot_exists(system):
    make_unhealthy(system)
    system.take_snapshot()          # only snapshot is unhealthy

    assert system.rollback() is False


def test_rollback_without_snapshots_fails(system):
    assert system.rollback() is False


def test_failed_rollback_is_logged(system):
    system.rollback()

    assert any(e.event_type == 'rollback_failed' for e in system.event_log)


# -- Rollback does not consume its history ----------------------------------


def test_rollback_preserves_the_snapshot(system):
    """Regression: pop() destroyed the rollback point after a single use."""
    system.take_snapshot()
    before = len(system.snapshots)

    system.rollback()

    assert len(system.snapshots) == before


def test_repeated_rollbacks_reach_the_same_state(system):
    system.take_snapshot()          # CPU=30

    results = []
    for _ in range(3):
        make_unhealthy(system)
        system.rollback()
        results.append(system.performance_metrics['CPU'])

    assert results == [30.0, 30.0, 30.0]


def test_rollback_count_is_tracked(system):
    system.take_snapshot()
    make_unhealthy(system)
    system.rollback()
    make_unhealthy(system)
    system.rollback()

    assert system.rollback_count == 2


def test_restored_metrics_are_a_copy(system):
    system.take_snapshot()
    make_unhealthy(system)
    system.rollback()

    system.performance_metrics['CPU'] = 999.0
    system.rollback()

    assert system.performance_metrics['CPU'] == 30.0


# -- Snapshot bookkeeping ---------------------------------------------------


def test_snapshot_records_health(system):
    healthy = system.take_snapshot()
    make_unhealthy(system)
    unhealthy = system.take_snapshot()

    assert healthy['healthy'] is True
    assert unhealthy['healthy'] is False


def test_snapshot_history_is_bounded(system):
    for i in range(50):
        system.performance_metrics['CPU'] = 30.0 + i * 0.1
        system.take_snapshot()

    assert len(system.snapshots) <= 10


def test_healthy_snapshot_count(system):
    system.take_snapshot()
    make_unhealthy(system)
    system.take_snapshot()

    assert system.healthy_snapshot_count() == 1


def test_is_healthy_reflects_thresholds(system):
    assert system.is_healthy() is True
    make_unhealthy(system)
    assert system.is_healthy() is False


def test_quantum_component_has_a_tighter_threshold():
    s = SelfHealingSystem()
    assert s.thresholds['Quantum'] < s.thresholds['CPU']


# -- Anomaly detection ------------------------------------------------------


def test_anomaly_reported_above_threshold(system):
    make_unhealthy(system)

    found = system.detect_anomalies()
    assert [a['component'] for a in found] == ['CPU']


def test_no_anomaly_within_threshold(system):
    assert system.detect_anomalies() == []


def test_severity_escalates_well_past_threshold(system):
    system.performance_metrics['CPU'] = 81.0
    warning = system.detect_anomalies()[0]
    system.performance_metrics['CPU'] = 200.0
    critical = system.detect_anomalies()[0]

    assert warning['severity'] == 'warning'
    assert critical['severity'] == 'critical'


def test_overflow_percentage_is_reported(system):
    system.performance_metrics['CPU'] = 160.0  # threshold is 80
    anomaly = system.detect_anomalies()[0]

    assert anomaly['overflow_pct'] == pytest.approx(100.0)
