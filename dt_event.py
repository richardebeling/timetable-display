#!/bin/python3

# Event classes for the dementia timetable program

from collections import namedtuple

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
    CONDITION_ODD  = 2

    def __init__(self):
        Event.__init__(self)
        self._times = []

    def addRecurringTime(self, dow, hour, minute, condition):
        t = RecurringTime(dow, hour, minute, condition)
        self._times.append(t)

    def getRecurringTimes(self):
        return self._times


class UniqueEvent(Event):
    def __init__(self):
        Event.__init__(self)
        self._times = []

    def addUniqueTime(self, day, month, year, hour, minute):
        t = UniqueTime(day, month, year, hour, minute)
        self._times.append(t)

    def getUniqueTimes(self):
        return self._times

