#!/bin/python3

# Event classes for the dementia timetable program

from collections import namedtuple
import datetime
from typing import List

UniqueTime = namedtuple("UniqueTime", "day month year hour minute")
RecurringTime = namedtuple("RecurringTime", "dow hour minute condition")


class Event:
    VALID_MODIFIERS = ["notime"]

    def __init__(self):
        self.description = ""
        self.modifiers = []


class RecurringEvent(Event):
    CONDITION_NONE = 0
    CONDITION_EVEN = 1
    CONDITION_ODD = 2

    def __init__(self):
        Event.__init__(self)
        self._times = []

    def add_recurring_time(self, t: RecurringTime) -> None:
        self._times.append(t)

    def get_recurring_times(self) -> list:
        return self._times

    @staticmethod
    def _date_matches_recurring_time(d: datetime.date, t: RecurringTime):
        c_met = False
        if t.condition == RecurringEvent.CONDITION_NONE:
            c_met = True
        elif t.condition == RecurringEvent.CONDITION_ODD:
            c_met = (d.isocalendar()[1] % 2 == 1)
        elif t.condition == RecurringEvent.CONDITION_EVEN:
            c_met = (d.isocalendar()[1] % 2 == 0)
        return (c_met and d.weekday() == t.dow)

    def get_next_renderevents(
            self, start: datetime.datetime,
            end: datetime.datetime) -> List[datetime.datetime]:
        date = start
        times = []

        while date < end:
            for time in self._times:
                if self._date_matches_recurring_time(date, time):
                    date = date.replace(hour=time.hour, minute=time.minute)
                    if date > start and date < end:
                        times.append(date)
            date = date + datetime.timedelta(days=1)

        events = []
        for time in times:
            e = RenderEvent
            e.time = time
            e.description = self.description

        return events


class UniqueEvent(Event):
    def __init__(self):
        Event.__init__(self)
        self._times = []

    def add_unique_time(self, t: UniqueTime) -> None:
        self._times.append(t)

    def get_unique_times(self) -> list:
        return self._times

    def get_next_renderevents(
            self, start: datetime.datetime,
            end: datetime.datetime) -> List[datetime.datetime]:
        times = []
        for time in self._times:
            dt = datetime.datetime(day=time.day, month=time.month,
                                   year=time.year, hour=time.hour,
                                   minute=time.minute)
            if dt > start and dt < end:
                times.append(dt)

        events = []
        for time in times:
            e = RenderEvent
            e.time = time
            e.description = self.description

        return events


class RenderEvent(Event):
    def __init__(self):
        Event.__init__(self)
        self.time = datetime.datetime.today()
        self.description = ""


class EventConverter():
    @staticmethod
    def get_render_list_from_unique(
            max_count: int,
            max_time: datetime.datetime,
            event: UniqueEvent
            ) -> List[RenderEvent]:
        print("test")

    @staticmethod
    def get_render_list_from_recurring(
            max_count: int,
            max_time: datetime.datetime,
            event: RecurringEvent
            ) -> List[RenderEvent]:
        print("test")
