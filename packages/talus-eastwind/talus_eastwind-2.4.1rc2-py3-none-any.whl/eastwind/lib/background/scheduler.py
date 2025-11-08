# -*- coding: utf-8 -*-
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .workload import (
    Workload,
)
from .trigger import (
    TimeTrigger,
    TimeTriggerInterval,
    TimeTriggerRepeatAt,

)

WEEKDAY_MAP: list[str] = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]


class Scheduler:
    def __init__(self, local_timezone: ZoneInfo, *args):
        self.__scheduler = AsyncIOScheduler(
            timezone=local_timezone,
        )
        self.__counter: int = 0
        self.__args = args

    def total_tasks(self) -> int:
        return self.__counter

    def add_task(self, workload: Workload, trigger: TimeTrigger):
        # Add the counter.
        self.__counter += 1
        # Add the task to scheduler, based on its trigger.
        # Interval Trigger.
        if isinstance(trigger, TimeTriggerInterval):
            self.__scheduler.add_job(self.run_task, "interval",
                                     weeks=trigger.week, days=trigger.day,
                                     hours=trigger.hour, minutes=trigger.minute, seconds=trigger.second,
                                     start_date=trigger.start_date, end_date=trigger.end_date,
                                     args=[workload])
            return
        # Cron Trigger
        if isinstance(trigger, TimeTriggerRepeatAt):
            self.__scheduler.add_job(self.run_task, "cron",
                                     month=trigger.month, day=trigger.day,
                                     week=trigger.week, day_of_week=None if trigger.week_day is None else WEEKDAY_MAP[trigger.week_day],
                                     hour=trigger.hour, minute=trigger.minute, second=trigger.second,
                                     start_date=trigger.start_date, end_date=trigger.end_date,
                                     args=[workload])
            return
        # Otherwise, raise an exception.
        raise NotImplementedError(f"unknown trigger type {type(trigger).__name__}")

    async def run_task(self, workload: Workload):
        await workload(*self.__args)

    def start(self):
        # Start the scheduler.
        self.__scheduler.start()

    def shutdown(self):
        # Shutdown the scheduler.
        self.__scheduler.shutdown()
