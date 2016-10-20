#!/usr/bin/python3

from dt_config import ConfigReader, ConfigCleaner
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import dt_settings

from threading import Event
from os import path
import time
from shutil import copyfile


class ConfigChangeHandler(FileSystemEventHandler):
<<<<<<< HEAD
    def __init__(self, filename, event_to_set):
        FileSystemEventHandler.__init__(self)
        self._filename = filename
        self._event = event_to_set
=======
    def __init__(self, filename, changeEvent):
        FileSystemEventHandler.__init__(self)
        self._filename = filename
        self._event = changeEvent
>>>>>>> bf755c8437e05fdd7b9dc7d4829edcd9f54e451a

    def on_modified(self, event: FileModifiedEvent) -> None:
        if event.is_directory:
            return
<<<<<<< HEAD
        if self._filename == path.abspath(event.src_path):
=======
        if self._filename in event.src_path:
>>>>>>> bf755c8437e05fdd7b9dc7d4829edcd9f54e451a
            self._event.set()


class DementiaTimetable():
    def __init__(self):
        self._log("Dementia Timetable started.")

        self._config_path = path.abspath(dt_settings.filename)
        if not path.isfile(self._config_path):
            raise Exception("Wrong config file given: " + dt_settings.filename)

        self._config_change_event = Event()
        self._config_change_event.set()  # trigger loading the config file

        # Trigger the event if the config file is changed
        self._log("Starting file monitor thread...")
        handler = ConfigChangeHandler(
                dt_settings.filename,
                self._config_change_event
                )
        self._observer = Observer()
<<<<<<< HEAD
        self._observer.schedule(handler, path.dirname(self._config_path))
=======
        self._observer.schedule(handler, self._config_path)
>>>>>>> bf755c8437e05fdd7b9dc7d4829edcd9f54e451a
        self._observer.start()

        self._reader = ConfigReader()
        self._cleaner = ConfigCleaner()
        self._cleaned_date = time.date.today()

        # todo: Renderer erstellen

    def _log(self, s: str) -> None:
        print(time.datetime.now().strftime("[%d.%m %H:%M:%S] ") + s)

    def _handle_config_change(self) -> None:
        new = ConfigReader()
        self._log("Config change detected. Reparsing...")
        try:
            new.parse(self._config_path)
        except Exception:
            self._log("!!! Error: Could not parse config file.")
            return
        self._reader.parse(self._config_path)

    def loop(self) -> None:
        # todo: Combine this loop with tkinter message system
        while(True):
            if self._config_change_event.isSet():
                self._handle_config_change()
                self._config_change_event.clear()

            if time.date.today() > self._cleaned_date:
                self._log("Date change detected. Cleaning...")
                copyfile(self._config_path, self._config_path + ".bak")
                try:
                    self._cleaner.clean(self._config_path)
                except Exception:
                    self._log("!!! Cleaning the config file failed.")
                #  config_change_event should be triggered automatically.
                self._cleaned_date = time.date.today()

            #  todo: Check for closed GUI

        self._log("Waiting for the file monitor thread to finish...")
        self._observer.join()


if __name__ == "__main__":
    table = DementiaTimetable()
    table.loop()
