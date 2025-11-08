# -*- coding: utf-8 -*-
from abc import ABC
from datetime import datetime


class TimeTrigger(ABC):
    pass


class TimeTriggerInterval(TimeTrigger):
    def __init__(self, week: int = 0, day: int = 0,
                 hour: int = 0, minute: int = 0, second: int = 0,
                 start_date: datetime | None = None,
                 end_date: datetime | None = None):
        self.week = week
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.start_date = start_date
        self.end_date = end_date


class TimeTriggerRepeatAt(TimeTrigger):
    def __init__(self, month: int = None, day: int = None,
                 week: int = None, week_day: int = None,
                 hour: int = None, minute: int = None, second: int = None,
                 start_date: datetime = None, end_date: datetime = None):
        self.month = month
        self.day = day
        self.week = week
        # 0 = SUN -> 6 = SAT, 7 = SUN
        self.week_day = week_day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.start_date = start_date
        self.end_date = end_date
