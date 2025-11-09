# streamlit_job_scheduler/tests/test_ui.py
import pytest
from streamlit_job_scheduler.models import SchedulerConfig, ScheduleInfo
from streamlit_job_scheduler.enums import ScheduleType

def import_scheduler_ui():
    from streamlit_job_scheduler.ui import job_scheduler
    return job_scheduler

def test_ui_runs_cron_job(monkeypatch):
    """Smoke test: ensure the cron UI runs and returns a valid result without errors."""
    config = SchedulerConfig(schedule_type=ScheduleType.CRONJOB, schedule="* * * * *")
    result = import_scheduler_ui()(config)
    assert isinstance(result, ScheduleInfo)
    assert result.schedule is not None


def test_ui_runs_one_time(monkeypatch):
    """Smoke test: ensure one-time UI runs and returns expected structure."""
    config = SchedulerConfig(schedule_type=ScheduleType.ONE_TIME, schedule="2024-12-31T23:59:00")
    print(config.schedule_type)
    result = import_scheduler_ui()(config)
    assert isinstance(result, ScheduleInfo)
    assert result.schedule is not None


def test_ui_invalid_config(monkeypatch):
    """Ensure invalid or empty config does not crash the UI."""
    config = SchedulerConfig(schedule_type=None)
    result = import_scheduler_ui()(config)
    assert isinstance(result, ScheduleInfo)
    assert result.schedule_type
