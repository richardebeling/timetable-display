#!/bin/python3

# Event classes for the dementia timetable program

from collections import namedtuple
from datetime import datetime, timedelta, date
from typing import List
from dt_execute import ExecutionEvent

UniqueTime = namedtuple("UniqueTime", "day month year hour minute")
RecurringTime = namedtuple("RecurringTime", "dow hour minute condition")
ExecutionTime = namedtuple("ExecutionTime", "offset executable")


class Event:
    VALID_MODIFIERS = ["notime", "until", "tomorrow", "padding", "exec",
                       "nodraw"]

    def __init__(self):
        self.description = ""
        self.modifiers = []
        self.execution_times = []


class SimpleEvent(Event):
    def __init__(self):
        Event.__init__(self)
        self.time = datetime.now()
        self.description = ""

    def timestring(self) -> str:
        return "{dt.hour}:{dt.minute:02}".format(dt=self.time)

    def get_execution_events(self) -> List[ExecutionEvent]:
        event_list = []
        for execution_time in self.execution_times:
            e = ExecutionEvent()
            e.time = self.time + timedelta(minutes=execution_time.offset)
            e.executable = execution_time.executable
            event_list.append(e)
        return event_list


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
    def _date_matches_recurring_time(d: date, t: RecurringTime):
        c_met = False
        if t.condition == RecurringEvent.CONDITION_NONE:
            c_met = True
        elif t.condition == RecurringEvent.CONDITION_ODD:
            c_met = (d.isocalendar()[1] % 2 == 1)
        elif t.condition == RecurringEvent.CONDITION_EVEN:
            c_met = (d.isocalendar()[1] % 2 == 0)
        return (c_met and d.isoweekday() == t.dow)

    def get_next_datetimes(self, start: datetime,
                           end: datetime) -> List[datetime]:
        date = start
        times = []
        while date < end:
            for time in self._times:
                if self._date_matches_recurring_time(date, time):
                    date = date.replace(hour=time.hour, minute=time.minute)
                    if date > start and date < end:
                        times.append(date)
            date = date + timedelta(days=1)
        return times

    def get_next_simpleevents(self, start: datetime,
                              end: datetime) -> List[SimpleEvent]:
        times = self.get_next_datetimes(start, end)
        events = []
        for time in times:
            e = SimpleEvent()
            e.time = time
            e.description = self.description
            e.modifiers = self.modifiers
            e.execution_times = self.execution_times
            events.append(e)
        return events


class UniqueEvent(Event):
    def __init__(self):
        Event.__init__(self)
        self._times = []

    def add_unique_time(self, t: UniqueTime) -> None:
        self._times.append(t)

    def get_unique_times(self) -> list:
        return self._times

    def get_next_datetimes(self, start: datetime,
                           end: datetime) -> List[datetime]:
        times = []
        for time in self._times:
            dt = datetime(day=time.day, month=time.month, year=time.year,
                          hour=time.hour, minute=time.minute)
            if dt > start and dt < end:
                times.append(dt)
        return times

    def get_next_simpleevents(self, start: datetime,
                              end: datetime) -> List[SimpleEvent]:
        times = self.get_next_datetimes(start, end)
        events = []
        for time in times:
            e = SimpleEvent()
            e.time = time
            e.description = self.description
            e.modifiers = self.modifiers
            e.execution_times = self.execution_times
            events.append(e)
        return events
