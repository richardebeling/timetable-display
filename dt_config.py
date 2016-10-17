#!/bin/python3

# Config parser for the dementia timetable program.
# For an example config file, see "example.cfg"

from dt_event import Event, UniqueEvent, RecurringEvent
from datetime import datetime


class ConfigReader:
    def __init__(self):
        self.general = {"uniquedateformat": "%H:%M-%d.%m.%Y"}
        self.recurring = []
        self.unique = []

    def _parseEventDescription(self, line: str, event: Event,
                               section: str) -> None:
        event.description = line
        if section == "recurring":
            self.recurring.append(event)
        elif section == "unique":
            self.unique.append(event)
        else:
            raise Exception("Inside unknown section: " + line)

    def _parseRecurringEventTimes(self, line: str) -> RecurringEvent:
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

                event.addRecurringTime(int(dow), int(hour), int(minute),
                                       condition)

            elif token.lower() in Event.VALID_MODIFIERS:
                event.modifiers.append(token.lower())

            else:
                raise Exception("Unknown identifier: " + token
                                + " in line: " + line)

        return event

    def _parseUniqueEventTimes(self, line: str,
                               dateformat: str) -> UniqueEvent:
        event = UniqueEvent()

        tokens = line.split()
        for token in tokens:
            token.strip()
            try:
                t = datetime.strptime(token, dateformat)
                event.addUniqueTime(t.day, t.month, t.year,
                                    t.hour, t.minute)
            except ValueError:
                raise Exception("Error parsing: " + token)

        return event

    def parse(self, filename: str) -> None:
        with open(filename) as f:
            section = "general"
            currentEvent = Event()
            expectingEventDescription = False

            for line in f.readlines():
                line = line.strip()
                if not line:
                    continue

                if expectingEventDescription:
                    self._parseEventDescription(line, currentEvent, section)
                    expectingEventDescription = False

                elif line[0] is '[' and line[-1] is ']':
                    section = line[1:-1]

                elif section == "general":
                    splits = line.split('=', 1)
                    self.general[splits[0].strip()] = splits[1].strip()

                elif section == "recurring":
                    currentEvent = self._parseRecurringEventTimes(line)
                    expectingEventDescription = True

                elif section == "unique":
                    currentEvent = self._parseUniqueEventTimes(
                            line,
                            self.general['uniquedateformat']
                    )
                    expectingEventDescription = True


class ConfigWriter():
    def _hasPassed(self, t: datetime) -> bool:
        n = datetime.now()
        return n > t

    def _getRecurringString(self, event: RecurringEvent) -> str:
        line = ""
        added = []
        times = event.getRecurringTimes()
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
                    if (inner not in added
                        and inner.hour == time.hour
                            and inner.minute == time.minute):
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

    def _getUniqueString(self, event: UniqueEvent, dateformat: str) -> str:
        line = ""
        added = []
        times = event.getUniqueTimes()
        firsttime = True

        for time in times:
            if time not in added:
                t = datetime(time.year, time.month, time.day,
                             time.hour, time.minute)

                if not self._hasPassed(t):

                    if not firsttime:
                        line += " "
                    else:
                        firsttime = False

                    line += t.strftime(dateformat)

                added.append(time)

        return line

    def _buildLines(self, general: dict,
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
            lines.append(self._getRecurringString(event))
            lines.append(event.description)
            lines.append("")
        lines.append("")

        lines.append("[unique]")
        for event in unique:
            lines.append(self._getUniqueString(event, dateformat))
            lines.append(event.description)
            lines.append("")

        return lines

    def write(self, filename: str, general: dict,
              recurring: list,
              unique: list) -> None:
        lines = self._buildLines(general, recurring, unique)
        with open(filename, 'w') as f:
            f.write('\n'.join(lines))


class ConfigCleaner(ConfigReader, ConfigWriter):
    def init(self):
        ConfigReader.init(self)
        ConfigWriter.init(self)

    def clean(self, filename) -> None:
        self.parse(filename)
        self.write(filename, self.general, self.recurring, self.unique)
