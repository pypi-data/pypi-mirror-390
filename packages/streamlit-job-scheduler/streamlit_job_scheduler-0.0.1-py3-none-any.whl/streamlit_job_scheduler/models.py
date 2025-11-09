from streamlit_job_scheduler.enums import ScheduleType

class SchedulerConfig:

    def __init__(self, schedule_type:ScheduleType = ScheduleType.CRONJOB, schedule=None, title="🕒 Schedule a Job", display_only: ScheduleType = None, show_schedule_type: bool = False):
        """
        schedule_type: "cron" or "one-time"
        schedule_time: datetime (for one-time)
        pre_config: dict (used to prefill cron UI)
        """
        self.title = title
        self.schedule_type = schedule_type.value if schedule_type else ScheduleType.CRONJOB.value
        self.schedule = schedule
        self.__pre_config = {}
        self.display_only = display_only
        self.show_schedule_type = show_schedule_type

    @property
    def pre_config(self):
        return self.__pre_config

class ScheduleInfo:
    def __init__(self, schedule_type: str, schedule: str):
        self.schedule_type = schedule_type
        self.schedule = schedule