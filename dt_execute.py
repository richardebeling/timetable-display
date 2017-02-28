#!/usr/bin/python3

import datetime
import subprocess
import threading


class ExecutionEvent:
    def __init__(self):
        self.time = datetime.datetime.now()
        self.executable = ''

    def appropriate(self) -> bool:
        return datetime.datetime.now() >= self.time

    def execute(self) -> None:
        subprocess.Popen(self.executable.split(' '))


class ExecutionManager:
    def __init__(self):
        self.events = []  # List of dt_event.ExecutionEvents
        self.event_lock = threading.Lock()
        self.events_changed = threading.Event()

    def _clean_and_sort_events(self) -> None:
        self.events.sort(key=lambda x: x.time)
        while self.events and self.events[0].appropriate():
            self.events.pop(0)

    def tick(self) -> None:
        with self.event_lock:
            if self.events_changed.isSet():
                self._clean_and_sort_events()
                self.events_changed.clear()

            while self.events:
                if not self.events[0].appropriate():
                    break
                try:
                    self.events[0].execute()
                finally:
                    self.events.pop(0)
