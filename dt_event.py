#!/bin/python3

# Event classes for the dementia timetable program

from collections import namedtuple
import datetime

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

    def addRecurringTime(self, t: RecurringTime) -> None:
        self._times.append(t)

    def getRecurringTimes(self) -> list:
        return self._times

    def _dateMatchesRecurringTime(d: datetime.date, t: RecurringTime):
        c_met = False
        if t.condition == RecurringEvent.CONDITION_NONE:
            c_met = True
        elif t.condition == RecurringEvent.CONDITION_ODD:
            c_met = (d.isocalendar()[1] % 2 == 1)
        elif t.condition == RecurringEvent.CONDITION_EVEN:
            c_met = (d.isocalendar()[1] % 2 == 0)
        return (c_met and d.weekday() == t.dow)

    def getNextTimes(self, start: datetime.datetime,
                     end: datetime.datetime) -> list[datetime.datetime]:
        date = start
        times = []

        while date < end:
            for time in self._times:
                if self._dateMatchesRecurringTime(date, time):
                    date = date.replace(hour=time.hour, minute=time.minute)
                    if date > start and date < end:
                        times.append(date)
            date = date + datetime.timedelta(days=1)


class UniqueEvent(Event):
    def __init__(self):
        Event.__init__(self)
        self._times = []

    def addUniqueTime(self, t: UniqueTime) -> None:
        self._times.append(t)

    def getUniqueTimes(self) -> list:
        return self._times

    def getNextTimes(self, start: datetime.datetime,
                     end: datetime.datetime) -> list[datetime.datetime]:
        # todo
        print("test")


class RenderEvent(Event):
    def __init__(self):
        Event.__init__(self)
        self.time = datetime.datetime.today()


class EventConverter():
    @staticmethod
    def getRenderListFromUnique(max_count: int, max_time: datetime.datetime,
                                event: UniqueEvent) -> list[RenderEvent]:
        print("test")

    @staticmethod
    def getRenderListFromRecurring(max_count: int, max_time: datetime.datetime,
                                   event: RecurringEvent) -> list[RenderEvent]:
        print("test")
