import streamlit as st
from datetime import datetime
from streamlit_job_scheduler.scheduler import (
    generate_cron_expr,
    describe_cron,
    parse_cron_to_preconfig,
)
from streamlit_job_scheduler.enums import ScheduleType
from streamlit_job_scheduler.models import SchedulerConfig, ScheduleInfo

def job_scheduler(callback_func, config: SchedulerConfig = None) -> ScheduleInfo:
    """
    Render a Streamlit-based UI to create a scheduled job (one-time or cron) and produce a ScheduleInfo.
    This function builds a small interactive scheduler UI using Streamlit widgets. It supports
    two scheduling modes: a one-time schedule (date + hour + minute) and a cron-style schedule
    (with several frequency presets and a custom cron expression). The created schedule is
    returned as a ScheduleInfo object or passed to a provided callback.
    Parameters
    ----------
    callback_func : Callable[[ScheduleInfo], Any] | None
        Optional. If provided and callable, the function will be invoked with the constructed
        ScheduleInfo object (job_data) whenever the UI produces a schedule. If omitted or not
        callable, this function returns the ScheduleInfo object directly.
    config : SchedulerConfig | None, optional
        Optional configuration object that controls initial UI state and appearance. Known
        fields used by this function include:
          - title: str - title rendered at top of the Streamlit page.
          - display_only: Optional[ScheduleType] - if set, the schedule type selection is
            displayed as a fixed type rather than an interactive control.
          - schedule_type: ScheduleType - initial schedule type used when not display_only.
          - schedule: Optional[str] - an existing cron expression used to prepopulate UI
            (parsed with parse_cron_to_preconfig).
          - show_schedule_type: bool - whether to render subheaders describing the selected
            schedule mode.
        If config is None, a default SchedulerConfig() is created.
    Returns
    -------
    ScheduleInfo | None
        If callback_func is not provided (or not callable), the function returns a ScheduleInfo
        instance describing the selected schedule:
          - For one-time schedules: ScheduleInfo(ScheduleType.ONE_TIME.value, run_time_iso)
            where run_time_iso is an ISO 8601 datetime string representing the selected date/time.
          - For cron schedules:   ScheduleInfo(ScheduleType.CRONJOB.value, cron_expression)
            where cron_expression is the generated cron string.
        If callback_func is provided and callable, the function invokes callback_func(job_data)
        and returns None (the return value is not used).
    Behavior and UI details
    -----------------------
    - Renders a Streamlit title using config.title.
    - If display_only is set in config, only that schedule type is used; otherwise the user can
      select between "One-Time" and "Cron Job" using a radio control.
    - One-time schedule UI:
        - Date input, hour selectbox (0-23), minute selectbox (0-59).
        - Displays a success message with the scheduled datetime and returns an ISO string.
    - Cron schedule UI:
        - Frequency presets: "Every X minutes", "Hourly", "Daily", "Weekly", "Monthly", "Custom".
        - Each preset exposes additional controls (e.g., minute interval, hours, minutes, weekdays,
          days-of-month) and calls generate_cron_expr(...) to build a cron expression.
        - The generated cron expression is shown in code format and a human-readable description
          is displayed using describe_cron(...).
        - Custom allows entering an arbitrary cron expression string which is passed to
          generate_cron_expr(frequency="Custom", custom_expr=...).
    - If config.schedule is provided it is parsed into pre_config by parse_cron_to_preconfig
      and used to set initial widget selections.
    Side effects
    ------------
    - Renders Streamlit UI components and messages (st.title, st.radio, st.date_input, st.selectbox,
      st.multiselect, st.number_input, st.text_input, st.markdown, st.code, st.success, etc.).
    - May call the provided callback_func with the resulting ScheduleInfo if callable.
    - Relies on external helper functions and types: SchedulerConfig, ScheduleInfo, ScheduleType,
      parse_cron_to_preconfig, generate_cron_expr, describe_cron.
    Examples
    --------
    - Typical usage returning the schedule:
        job = job_scheduler(None)
        # job is a ScheduleInfo object describing the user's selection
    - Typical usage with a callback:
        def on_schedule_created(schedule_info):
            # persist or enqueue schedule_info
            ...
        job_scheduler(on_schedule_created, config=my_config)
    Notes
    -----
    - This function must be executed within a Streamlit app context (i.e., inside streamlit
      script execution); it will not function correctly in a non-Streamlit environment.
    - The function does not perform validation beyond what the Streamlit widgets and the
      helper functions provide; consumers should validate ScheduleInfo values if necessary.
    """
    
    config = config or SchedulerConfig()
    pre_config = parse_cron_to_preconfig(config.schedule) if config.schedule else {}
    st.title(config.title)
    if config.display_only:
        schedule_type = config.display_only.value
    else:
        schedule_type = st.radio("Select Schedule Type", [ScheduleType.ONE_TIME.value, ScheduleType.CRONJOB.value],
                             index=0 if config.schedule_type == ScheduleType.ONE_TIME.value else 1)

    job_data = {}
    if schedule_type == ScheduleType.ONE_TIME.value:
        if config.show_schedule_type:
            st.subheader("📅 One-Time Schedule")

        date = st.date_input("Select Date", value=datetime.now().date())
        hour = st.selectbox("Hour", list(range(0, 24)), index=datetime.now().hour)
        minute = st.selectbox("Minute", list(range(0, 60)), index=datetime.now().minute)

        run_time = datetime.combine(date, datetime.min.time()).replace(hour=hour, minute=minute)

        st.success(f"Job will run once at **{run_time.strftime('%Y-%m-%d %H:%M')}**")

        job_data = ScheduleInfo(ScheduleType.ONE_TIME.value,run_time.isoformat())

    else:
        if config.show_schedule_type:
            st.subheader("🔁 Cron Job Schedule")

        frequency = st.selectbox(
            "Select Frequency",
            ["Every X minutes", "Hourly", "Daily", "Weekly", "Monthly", "Custom"],
            index=["Every X minutes", "Hourly", "Daily", "Weekly", "Monthly", "Custom"].index(
                pre_config.get("frequency", "Daily")
            )
        )

        cron_expr = ""

        if frequency == "Every X minutes":
            m = st.number_input("Every how many minutes?", 1, 60, 5)
            cron_expr = generate_cron_expr(frequency, minutes=m)

        elif frequency == "Hourly":
            h = st.number_input("Every how many hours?", 1, 24, 1)
            cron_expr = generate_cron_expr(frequency, hours=h)

        elif frequency == "Daily":
            hours = st.multiselect("Hours (0-23)", list(range(24)), default=[9, 17])
            minutes = st.multiselect("Minutes (0-59)", list(range(0, 60, 5)), default=[0])
            cron_expr = generate_cron_expr(frequency, hours=hours, minutes=minutes)

        elif frequency == "Weekly":
            days = st.multiselect(
                "Days",
                ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                default=["Monday"]
            )
            day_map = {"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3,
                       "Thursday": 4, "Friday": 5, "Saturday": 6}
            hours = st.multiselect("Hours (0-23)", list(range(24)), default=[9])
            minutes = st.multiselect("Minutes (0-59)", list(range(0, 60, 15)), default=[0])
            cron_expr = generate_cron_expr(
                frequency, weekdays=[day_map[d] for d in days], hours=hours, minutes=minutes
            )

        elif frequency == "Monthly":
            days = st.multiselect("Days (1-31)", list(range(1, 32)), default=[1, 15])
            hours = st.multiselect("Hours (0-23)", list(range(24)), default=[9])
            minutes = st.multiselect("Minutes (0-59)", list(range(0, 60, 15)), default=[0])
            cron_expr = generate_cron_expr(frequency, days=days, hours=hours, minutes=minutes)

        elif frequency == "Custom":
            expr = st.text_input("Custom Cron Expression", "*/5 * * * *")
            cron_expr = generate_cron_expr(frequency, custom_expr=expr)

        st.markdown("**🧠 Generated Cron:**")
        st.code(cron_expr)

        readable = describe_cron(cron_expr)
        st.success(f"🗓️ {readable}")

        job_data = ScheduleInfo(ScheduleType.CRONJOB.value, cron_expr)
    if callback_func and callable(callback_func):
        callback_func(job_data)
    else:
        return job_data

if __name__ == "__main__":
    job_scheduler(None)