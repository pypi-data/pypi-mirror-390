import pytest
from streamlit_job_scheduler.scheduler import (
    generate_cron_expr,
    describe_cron,
)

def test_generate_cron_expr_combined_daily():
    result = generate_cron_expr("Daily", hours=[8, 12], minutes=[0, 30])
    assert result == "0,30 8,12 * * *"

def test_generate_cron_expr_combined_weekly():
    result = generate_cron_expr("Weekly", weekdays=[1, 3], hours=[9], minutes=[0, 30])
    assert result == "0,30 9 * * 1,3"

def test_generate_cron_expr_combined_monthly():
    result = generate_cron_expr("Monthly", days=[1, 15], hours=[9], minutes=[30])
    assert result == "30 9 1,15 * *"

def test_describe_cron_daily():
    expr = "0,30 9,17 * * *"
    result = describe_cron(expr)
    assert "Runs daily" in result
    assert "09:00" in result
    assert "17:30" in result

def test_describe_cron_weekly():
    expr = "0 10 * * 1,3"
    result = describe_cron(expr)
    assert "Mon" in result and "Wed" in result

def test_describe_cron_monthly():
    expr = "30 9 1,15 * *"
    result = describe_cron(expr)
    assert "every month" in result

def test_describe_cron_every_x_minutes():
    expr = "*/10 * * * *"
    result = describe_cron(expr)
    assert "every 10 minute" in result

def test_describe_cron_invalid():
    expr = "invalid cron"
    result = describe_cron(expr)
    assert "Invalid" in result or "Could not" in result
