import os
import json
import re
from typing import Dict, Any, List, Optional

def is_valid_cron(expr: str) -> bool:
    """Check if a cron expression has exactly 5 fields."""
    parts = expr.split()
    return len(parts) == 5

def join(values, default="*"):
    """Join multiple integers into a comma-separated string or return * if empty."""
    if not values:
        return default
    return ",".join(str(v) for v in sorted(set(values)))

def generate_cron_expr(frequency, **kwargs):
    """Generate a single cron expression string for multiple selections."""
    if frequency == "Every X minutes":
        return f"*/{kwargs.get('minutes', 5)} * * * *"

    elif frequency == "Hourly":
        return f"0 */{kwargs.get('hours', 1)} * * *"

    elif frequency == "Daily":
        hours = join(kwargs.get("hours", [0]))
        minutes = join(kwargs.get("minutes", [0]))
        return f"{minutes} {hours} * * *"

    elif frequency == "Weekly":
        weekdays = join(kwargs.get("weekdays", [0]))
        hours = join(kwargs.get("hours", [0]))
        minutes = join(kwargs.get("minutes", [0]))
        return f"{minutes} {hours} * * {weekdays}"

    elif frequency == "Monthly":
        days = join(kwargs.get("days", [1]))
        hours = join(kwargs.get("hours", [0]))
        minutes = join(kwargs.get("minutes", [0]))
        return f"{minutes} {hours} {days} * *"

    elif frequency == "Custom":
        return kwargs.get("custom_expr", "*/5 * * * *")

    return "* * * * *"

def parse_cron_to_preconfig(cron_expr: str) -> Dict[str, Any]:
    """
    Parse a standard 5-field cron expression into a SchedulerConfig-style pre_config dict.
    
    Examples:
        "0 9 * * *" -> {"frequency": "Daily", "hours": [9], "minutes": [0]}
        "0,30 8,12 * * 1,3" -> {"frequency": "Weekly", "weekdays": [1,3], "hours": [8,12], "minutes": [0,30]}
        "15 10 1,15 * *" -> {"frequency": "Monthly", "days": [1,15], "hours": [10], "minutes": [15]}
        "*/10 * * * *" -> {"frequency": "Every X minutes", "every_n_minutes": 10}
    """

    if not cron_expr or not isinstance(cron_expr, str):
        return {}

    fields = cron_expr.strip().split()
    if len(fields) != 5:
        return {}

    minute_field, hour_field, day_field, month_field, weekday_field = fields
    pre_config: Dict[str, Any] = {}

    # Helper to parse a comma-separated or range field into integers
    def parse_list(field: str) -> List[int]:
        if field in ["*", "?"]:
            return []
        result = []
        for part in field.split(","):
            if part.isdigit():
                result.append(int(part))
            elif "-" in part:
                start, end = part.split("-")
                result.extend(range(int(start), int(end) + 1))
        return result

    # Case: every N minutes
    if re.match(r"\*/(\d+)", minute_field):
        every_n = int(re.match(r"\*/(\d+)", minute_field).group(1))
        pre_config["frequency"] = "Every X minutes"
        pre_config["every_n_minutes"] = every_n
        return pre_config

    minutes = parse_list(minute_field)
    hours = parse_list(hour_field)
    days = parse_list(day_field)
    weekdays = parse_list(weekday_field)

    # Determine frequency
    if days and not weekdays:
        pre_config["frequency"] = "Monthly"
        pre_config["days"] = days
    elif weekdays and not days:
        pre_config["frequency"] = "Weekly"
        pre_config["weekdays"] = weekdays
    elif not days and not weekdays:
        pre_config["frequency"] = "Daily"
    else:
        pre_config["frequency"] = "Custom"

    if hours:
        pre_config["hours"] = hours
    if minutes:
        pre_config["minutes"] = minutes

    return pre_config

def describe_cron(expr: str) -> str:
    """Convert a cron expression into a human-readable description."""
    try:
        parts = expr.split()
        if len(parts) != 5:
            return "Invalid cron expression"

        minute, hour, day, month, weekday = parts

        def parse_list(field):
            if field == "*":
                return None
            return [int(x) for x in field.split(",") if x.isdigit()]

        minutes = parse_list(minute)
        hours = parse_list(hour)
        days = parse_list(day)
        weekdays = parse_list(weekday)

        # Time formatting
        if hours and minutes:
            times = [f"{h:02d}:{m:02d}" for h in hours for m in minutes]
        elif hours:
            times = [f"{h:02d}:00" for h in hours]
        else:
            times = ["every minute"]

        time_str = ", ".join(times)

        # Build readable description
        if day != "*" and weekday == "*":
            desc = f"Runs on day(s) {day} of every month at {time_str}"
        elif weekday != "*" and day == "*":
            weekday_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            days_text = ", ".join(weekday_names[d] for d in weekdays)
            desc = f"Runs every {days_text} at {time_str}"
        elif "*/" in minute:
            n = minute.replace("*/", "")
            desc = f"Runs every {n} minute(s)"
        elif "*/" in hour:
            n = hour.replace("*/", "")
            desc = f"Runs every {n} hour(s)"
        else:
            desc = f"Runs daily at {time_str}"

        return desc
    except Exception:
        return "Could not parse schedule"

