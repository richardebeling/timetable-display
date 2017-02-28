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

    def execute_if_appropriate(self) -> bool:
        if self.appropriate():
            self._execute()
            return True
        else:
            return False

    def _execute(self) -> None:
        subprocess.Popen(self.executable)


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

            while self.events and self.events[0].execute_if_appropriate():
                self.events.pop(0)
