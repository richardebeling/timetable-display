#!/usr/bin/python3

from dt_config import ConfigReader, ConfigCleaner
import dt_settings
from dt_renderer import TableRenderer

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

import traceback
import threading
import datetime
from os import path
from time import sleep
from shutil import copyfile

# Hardcoded settings:
UPDATE_THREAD_SLEEP_TIME = 0.5


class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, filename, event_to_set):
        FileSystemEventHandler.__init__(self)
        self._filename = filename
        self._event = event_to_set

    def on_modified(self, event: FileModifiedEvent) -> None:
        if event.is_directory:
            return
        if self._filename == path.abspath(event.src_path):
            self._event.set()


class DementiaTimetable():
    def __init__(self):
        self._log("Dementia Timetable started.")

        self._config_path = path.abspath(dt_settings.filename)
        if not path.isfile(self._config_path):
            raise Exception("Wrong config file given: " + dt_settings.filename)

        self._config_change_event = threading.Event()
        self._config_change_event.set()  # trigger loading the config file

        # Trigger the event if the config file is changed
        self._log("Starting file monitor thread...")
        handler = ConfigChangeHandler(
                dt_settings.filename,
                self._config_change_event
                )
        self._observer = Observer()
        self._observer.schedule(handler, path.dirname(self._config_path))
        self._observer.start()

        self._reader = ConfigReader()
        self._cleaner = ConfigCleaner()
        self._cleaned_date = datetime.date.today()

        self._renderer = TableRenderer()
        # renderer will be filled when config is reloaded

        self._update_thread = threading.Thread(target=self.update_loop)
        self._stop_update_thread = threading.Event()

    def _log(self, s: str) -> None:
        print(datetime.datetime.now().strftime("[%d.%m %H:%M:%S] ") + s)

    def _handle_config_change(self) -> None:
        new = ConfigReader()
        self._log("Config change detected. Reparsing...")
        try:
            new.parse(self._config_path)
        except Exception:
            self._log("!!! Error: Could not parse config file.")
            traceback.print_exc()
            return
        self._reader.parse(self._config_path)

        if 'Head' in self._reader.general:
            self._renderer.set_header_text(self._reader.general['Head'])
        if 'Foot' in self._reader.general:
            self._renderer.set_footer_text(self._reader.general['Foot'])

        events = []
        t1 = datetime.datetime.now()
        t2 = t1 + datetime.timedelta(days=3)
        for recurring_event in self._reader.recurring:
            events = recurring_event.get_next_renderevents(t1, t2)
        for unique_event in self._reader.unique:
            events = events + unique_event.get_next_renderevents(t1, t2)

        with self._renderer.event_lock:
            self._renderer.events = events
        self._renderer.events_changed()

    def mainloop(self) -> None:
        self._update_thread.start()
        self._renderer.mainloop()

        self._observer.stop()
        self._stop_update_thread.set()

        self._log("Waiting for the file monitor thread to finish...")
        self._observer.join()
        self._log("Waiting for the update thread to finish...")
        self._update_thread.join()

    def update_loop(self) -> None:
        while not self._stop_update_thread.isSet():
            if self._config_change_event.isSet():
                self._handle_config_change()
                self._config_change_event.clear()

            if datetime.date.today() > self._cleaned_date:
                self._log("Date change detected. Cleaning...")
                copyfile(self._config_path, self._config_path + ".bak")
                try:
                    self._cleaner.clean(self._config_path)
                except Exception:
                    self._log("!!! Cleaning the config file failed.")
                #  config_change_event should be triggered automatically.
                self._cleaned_date = datetime.date.today()

            sleep(UPDATE_THREAD_SLEEP_TIME)


if __name__ == "__main__":
    table = DementiaTimetable()
    table.mainloop()
