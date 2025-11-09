# Streamlit Job Scheduler

A simple and interactive Streamlit-based UI to configure and manage scheduled jobs — either **one-time** or **cron-based**.

## Features

- One-time scheduling (date + time + minute)
- Cron scheduling with flexible frequency (daily, weekly, monthly, etc.)
- Multi-hour and multi-day support in a single cron expression
- Human-readable cron descriptions
- Pytest unit tests



## Quick start

Install (editable during development) and run the Streamlit app:

```bash
pip install -e .
streamlit run -m streamlit_job_scheduler/ui.py
```

Or run directly (development):

```bash
python -m streamlit_job_scheduler/ui.py
```
### 🧩 Usage

```bash
pip install streamlit-job-scheduler
```
## Programmatic usage

Primary UI entry is [`streamlit_job_scheduler.ui.job_scheduler`](streamlit_job_scheduler/ui.py). Signature:

- job_scheduler(callback_func, config: SchedulerConfig = None) -> ScheduleInfo | None

- `callback_func`: optional callable that will be invoked with a [`streamlit_job_scheduler.models.ScheduleInfo`](streamlit_job_scheduler/models.py) when the user finalizes a schedule.
- `config`: optional [`streamlit_job_scheduler.models.SchedulerConfig`](streamlit_job_scheduler/models.py) to control initial UI state, title, pre-filled cron (parsed by [`streamlit_job_scheduler.scheduler.parse_cron_to_preconfig`](streamlit_job_scheduler/scheduler.py)), and display options.

Example (use inside a Streamlit session):

```py
from streamlit_job_scheduler.ui import job_scheduler
from streamlit_job_scheduler.models import SchedulerConfig
from streamlit_job_scheduler.enums import ScheduleType

config = SchedulerConfig(schedule_type=ScheduleType.CRONJOB, schedule="*/10 * * * *")
job = job_scheduler(None, config=config)  # returns a ScheduleInfo when not using a callback
```

Returned object is a [`streamlit_job_scheduler.models.ScheduleInfo`](streamlit_job_scheduler/models.py) with `.schedule_type` and `.schedule` attributes.

## Cron helpers

- generate_cron_expr(frequency, ...) — build a cron expression for frequencies like "Every X minutes", "Hourly", "Daily", "Weekly", "Monthly", or "Custom". See implementation: [streamlit_job_scheduler/scheduler.py](streamlit_job_scheduler/scheduler.py) and symbol: [`streamlit_job_scheduler.scheduler.generate_cron_expr`](streamlit_job_scheduler/scheduler.py)

- describe_cron(expr) — turn a standard 5-field cron into a human-friendly description. See: [`streamlit_job_scheduler.scheduler.describe_cron`](streamlit_job_scheduler/scheduler.py)

- parse_cron_to_preconfig(cron_expr) — parse a cron expression into a dict suitable for pre-filling the UI. See: [`streamlit_job_scheduler.scheduler.parse_cron_to_preconfig`](streamlit_job_scheduler/scheduler.py)

Example:

```py
from streamlit_job_scheduler.scheduler import generate_cron_expr, describe_cron

expr = generate_cron_expr("Daily", hours=[9,17], minutes=[0,30])
print(expr)                 # -> "0,30 9,17 * * *"
print(describe_cron(expr))  # human readable description
```

## Tests

Pytest tests cover scheduler logic and a smoke UI test harness.

Run tests:

```bash
pytest -q
```

Tests to review:
- [streamlit_job_scheduler/tests/test_scheduler.py](streamlit_job_scheduler/tests/test_scheduler.py)
- [streamlit_job_scheduler/tests/test_ui.py](streamlit_job_scheduler/tests/test_ui.py)

## Development notes & gotchas

- The package requires Streamlit (see [setup.cfg](setup.cfg) and [pyproject.toml](pyproject.toml)).
- The UI function is designed to be run inside a Streamlit app — running it outside Streamlit will not render widgets.
- The UI function signature is `job_scheduler(callback_func, config=None)`. When using programmatically prefer passing the config as the second positional argument or as a keyword (`config=...`) so the function can detect the callback and config correctly. See implementation: [`streamlit_job_scheduler.ui.job_scheduler`](streamlit_job_scheduler/ui.py)
- Cron parsing expects standard 5-field cron expressions (minute hour day month weekday). See: [`streamlit_job_scheduler.scheduler.is_valid_cron`](streamlit_job_scheduler/scheduler.py)

## Contributing

- Modify code in `streamlit_job_scheduler/` and add tests in `streamlit_job_scheduler/tests/`.
- Run tests with `pytest`.
- Keep examples and README in sync with code in:
  - [streamlit_job_scheduler/ui.py](streamlit_job_scheduler/ui.py)
  - [streamlit_job_scheduler/scheduler.py](streamlit_job_scheduler/scheduler.py)
  - [streamlit_job_scheduler/models.py](streamlit_job_scheduler/models.py)
  - [streamlit_job_scheduler/enums.py](streamlit_job_scheduler/enums.py)

## License
MIT — see [LICENSE](LICENSE)