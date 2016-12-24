#!/usr/bin/python3

from freezegun import freeze_time

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

    def _apply_general_section(self) -> None:
        renderer = self._renderer
        general = self._reader.general

        if 'head' in general:
            renderer.texts['head'] = general['head']
        if 'foot' in general:
            renderer.texts['foot'] = general['foot']
        if 'tomorrow' in general:
            renderer.texts['tomorrow'] = general['tomorrow']
        if 'today' in general:
            renderer.texts['today'] = general['today']

        if 'untiltext' in general:
            renderer.texts['untiltext'] = general['untiltext']

        if 'todaycount' in general:
            renderer.count_today = int(general['todaycount'])
        if 'tomorrowcount' in general:
            renderer.count_tomorrow = int(general['tomorrowcount'])

        if 'font' in general:
            renderer.font['name'] = general['font']
        if 'fontsize' in general:
            renderer.font['size'] = int(general['fontsize'])
        if 'fontbold' in general:
            renderer.font['bold'] = int(general['fontbold'])
        if 'fontitalics' in general:
            renderer.font['italics'] = bool(int(general['fontitalics']))
        if 'fontunderlined' in general:
            renderer.font['underlined'] = bool(int(general['fontunderlined']))
        if 'paddingsize' in general:
            renderer.font['paddingsize'] = int(general['paddingsize'])

        if 'bg' in general:
            renderer.colors['bg'] = general['bg']
        if 'fg' in general:
            renderer.colors['fg'] = general['fg']
        if 'hbg' in general:
            renderer.colors['hbg'] = general['hbg']
        if 'hfg' in general:
            renderer.colors['hfg'] = general['hfg']
        if 'pbg' in general:
            renderer.colors['pbg'] = general['pbg']
        if 'pfg' in general:
            renderer.colors['pfg'] = general['pfg']

        if 'arrow' in general:
            renderer.load_arrow_image(general['arrow'])

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

        self._apply_general_section()

        events = []
        t1 = datetime.datetime.now().replace(hour=0, minute=0, second=0)
        t2 = t1 + datetime.timedelta(days=3)
        for recurring_event in self._reader.recurring:
            events = events + recurring_event.get_next_renderevents(t1, t2)
        for unique_event in self._reader.unique:
            events = events + unique_event.get_next_renderevents(t1, t2)

        with self._renderer.event_lock:
            self._renderer.events = events
        self._renderer.events_changed()

    # todo: Remove
    @freeze_time("2016-12-22 09:30")
    def mainloop(self) -> None:
        self._update_thread.start()
        self._renderer.mainloop()

        self._stop_update_thread.set()

        # todo: sometimes deadlock, not ending the thread shouldn't cause
        # a problem though
        # self._log("Waiting for the file monitor thread to finish...")
        # self._observer.stop()
        # self._observer.join()
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

            sleep(dt_settings.updatethread_sleeptime_s)


if __name__ == "__main__":
    table = DementiaTimetable()
    table.mainloop()
