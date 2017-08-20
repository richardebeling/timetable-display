#!/bin/python3

# Config parser for the dementia timetable program.
# For an example config file, see "example.cfg"

from dt_event import Event
from dt_event import UniqueEvent, UniqueTime
from dt_event import RecurringEvent, RecurringTime, ExecutionTime
from datetime import datetime
from collections import OrderedDict
import re


class ConfigReader:
    execution_pattern = re.compile(r"(\+|\-)\s*(\d+)\s*([^+-]+)(?:\s|$)")

    def __init__(self):
        self.general = OrderedDict(uniquedateformat="%H:%M-%d.%m.%Y")
        self.recurring = []
        self.unique = []

    def _finish_event(self, line: str, event: Event, section: str) -> None:
        if section == "recurring":
            self.recurring.append(event)
        elif section == "unique":
            self.unique.append(event)
        else:
            raise Exception("Inside unknown section: " + line)

    def _parse_event_description(self, line: str, event: Event) -> None:
        event.description = line

    def _parse_execution_line(self, line: str, event: Event) -> None:
        res = ConfigReader.execution_pattern.split(line)
        res = res[1:]  # omit the first empty string
        offset = 1
        expectingTime = False
        expectingExecutable = False
        for group in res:
            if not group:  # empty strings between matches
                continue

            if expectingTime:
                if "+" in group or "-" in group:
                    raise Exception("Invalid character: " + line)
                offset = offset * int(group)
                expectingExecutable = True
                expectingTime = False

            elif expectingExecutable:
                if "+" in group or "-" in group:
                    raise Exception("Invalid character: " + line)
                # finished here:
                event.execution_times.append(ExecutionTime(offset, group))
                expectingExecutable = False

            else:  # expecting sign
                offset = int(group + "1")  # first just store sign
                expectingTime = True

    def _parse_recurring_event_times(self, line: str) -> RecurringEvent:
        hour = -1
        minute = -1
        event = RecurringEvent()

        tokens = line.split()
        for token in tokens:
            if ':' in token:  # time
                split = token.split(':')
                hour = split[0]
                minute = split[1]

            elif len(token) <= 2:  # day of week
                condition = RecurringEvent.CONDITION_NONE
                if len(token) == 2:
                    # gerade Wochenzahl / even week number
                    if token[0] == 'g' or token[0] == 'e':
                        condition = RecurringEvent.CONDITION_EVEN
                    # ungerade Wochenzahl / odd week number
                    elif token[0] == 'u' or token[0] == 'o':
                        condition = RecurringEvent.CONDITION_ODD
                    else:
                        raise Exception("Unkown day condition: " + token)
                    dow = token[1:]
                elif len(token) == 1:
                    dow = token

                t = RecurringTime(int(dow), int(hour), int(minute), condition)
                event.add_recurring_time(t)

            elif token.lower() in Event.VALID_MODIFIERS:
                event.modifiers.append(token.lower())

            else:
                raise Exception("Unknown identifier: " + token +
                                " in line: " + line)

        return event

    def _parse_unique_event_times(self, line: str,
                                  dateformat: str) -> UniqueEvent:
        event = UniqueEvent()

        tokens = line.split()
        for token in tokens:
            token.strip()
            if token in Event.VALID_MODIFIERS:
                event.modifiers.append(token)
            else:
                try:
                    d = datetime.strptime(token, dateformat)
                    t = UniqueTime(d.day, d.month, d.year, d.hour, d.minute)
                    event.add_unique_time(t)
                except ValueError:
                    raise Exception("Error parsing: " + token)

        return event

    def parse(self, filename: str, encoding: str) -> None:
        self.recurring = []
        self.unique = []
        with open(filename, "r", encoding=encoding) as f:
            section = "general"
            currentEvent = Event()
            expectingEventDescription = False
            expectingExecutionLine = False
            eventDone = False

            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue

                if expectingEventDescription:
                    self._parse_event_description(line, currentEvent)
                    expectingEventDescription = False

                    expectingExecutionLine = "exec" in currentEvent.modifiers
                    eventDone = not expectingExecutionLine

                elif expectingExecutionLine:
                    self._parse_execution_line(line, currentEvent)
                    expectingExecutionLine = False
                    eventDone = True

                elif line[0] is '[' and line[-1] is ']':
                    section = line[1:-1]

                elif section == "general":
                    splits = line.split('=', maxsplit=1)
                    if len(splits) == 2:
                        key = splits[0].strip().lower()
                        self.general[key] = splits[1].strip()
                    else:
                        raise Exception("Invalid general line: " + line)

                elif section == "recurring":
                    currentEvent = self._parse_recurring_event_times(line)
                    expectingEventDescription = True

                elif section == "unique":
                    currentEvent = self._parse_unique_event_times(
                            line,
                            self.general['uniquedateformat']
                    )
                    expectingEventDescription = True

                if eventDone:
                    self._finish_event(line, currentEvent, section)
                    eventDone = False


class ConfigWriter():
    def _has_passed(self, t: datetime) -> bool:
        n = datetime.now()
        return n > t

    def _get_recurring_string(self, event: RecurringEvent) -> str:
        line = ""
        added = []
        times = event.get_recurring_times()
        firsttime = True

        for time in times:
            if time not in added:
                if not firsttime:
                    line += " "
                else:
                    firsttime = False

                line += str(time.hour).zfill(2) + ":"
                line += str(time.minute).zfill(2) + " "
                if time.condition == RecurringEvent.CONDITION_EVEN:
                    line += "g"
                elif time.condition == RecurringEvent.CONDITION_ODD:
                    line += "u"
                elif not time.condition == RecurringEvent.CONDITION_NONE:
                    raise("Fehler")

                line += str(time.dow)
                added.append(time)

                for inner in times:
                    if (inner not in added and
                            inner.hour == time.hour and
                            inner.minute == time.minute):
                        line += " "
                        if inner.condition == RecurringEvent.CONDITION_EVEN:
                            line += "g"
                        elif inner.condition == RecurringEvent.CONDITION_ODD:
                            line += "u"
                        elif inner.condition != RecurringEvent.CONDITION_NONE:
                            raise("Fehler")
                        line += str(inner.dow)
                        added.append(inner)

        for modifier in event.modifiers:
            line += " " + modifier

        return line

    def _get_unique_string(self, event: UniqueEvent, dateformat: str) -> str:
        line = ""
        added = []
        times = event.get_unique_times()
        firsttime = True

        for time in times:
            if time not in added:
                t = datetime(time.year, time.month, time.day,
                             time.hour, time.minute)

                if not self._has_passed(t):

                    if not firsttime:
                        line += " "
                    else:
                        firsttime = False

                    line += t.strftime(dateformat)

                added.append(time)

        return line

    def _get_executions_string(self, event: Event) -> str:
        line = ""

        for time in event.execution_times:
            if time.offset >= 0:
                line += "+"
            line += str(time.offset) + " " + time.executable + " "

        return line

    def _build_lines(self, general: dict,
                     recurring: list,
                     unique: list) -> list:
        lines = []
        dateformat = general["uniquedateformat"]

        lines.append("[general]")
        for key in general:
            lines.append(key + " = " + general[key])
        lines.append("")
        lines.append("")

        lines.append("[recurring]")
        for event in recurring:
            lines.append(self._get_recurring_string(event))
            lines.append(event.description)
            if "exec" in event.modifiers:
                lines.append(self._get_executions_string(event))
            lines.append("")
        lines.append("")

        lines.append("[unique]")
        for event in unique:
            lines.append(self._get_unique_string(event, dateformat))
            lines.append(event.description)
            if "exec" in event.modifiers:
                lines.append(self._get_executions_string(event))
            lines.append("")

        return lines

    def write(self, filename: str, general: dict,
              recurring: list,
              unique: list, encoding: str) -> None:
        lines = self._build_lines(general, recurring, unique)
        with open(filename, 'w', encoding=encoding) as f:
            f.write('\n'.join(lines))


class ConfigCleaner(ConfigReader, ConfigWriter):
    def init(self):
        ConfigReader.init(self)
        ConfigWriter.init(self)

    def clean(self, filename: str, encoding: str) -> None:
        self.parse(filename, encoding)
        self.write(filename, self.general, self.recurring, self.unique,
                   encoding)
