#!/usr/bin/python3

from dt_config import ConfigReader, ConfigCleaner
import dt_settings
from dt_renderer import TableRenderer
from dt_execute import ExecutionManager

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

import traceback
import threading
import datetime
import locale
import argparse
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
        if path.abspath(self._filename) == path.abspath(event.src_path):
            self._event.set()


class DementiaTimetable():
    def __init__(self, fullscreen):
        self._log("Dementia Timetable started.")
        if fullscreen:
            self._log("Starting in fullscreen mode.")

        self._config_path = path.abspath(dt_settings.filename)
        if not path.isfile(self._config_path):
            raise Exception("Wrong config file given: " + dt_settings.filename)

        self._config_change_event = threading.Event()
        self._config_change_event.set()      # trigger loading the config file

        self._renderer_preview_timespan = 5  # days
        self._update_event = threading.Event()

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

        self._renderer = TableRenderer(fullscreen)
        # renderer will be filled when config is reloaded

        self._execution_manager = ExecutionManager()

        self._update_thread = threading.Thread(target=self.update_loop)
        self._stop_update_thread = threading.Event()

    def _log(self, s: str) -> None:
        print(datetime.datetime.now().strftime("[%d.%m %H:%M:%S] ") + s)

    def _apply_general_section(self) -> None:
        renderer = self._renderer
        general = self._reader.general  # dict of (variable, value) pairs

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
        if 'hilightafter' in general:
            renderer.hilight_after = int(general['hilightafter'])
        if 'showclock' in general:
            renderer.show_clock = bool(general['showclock'])
        if 'hideuntilwhendone' in general:
            renderer.hide_until_when_done = bool(general['hideuntilwhendone'])

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
            new.parse(self._config_path, dt_settings.fileencoding)
        except Exception:
            self._log("!!! Error: Could not parse config file.")
            traceback.print_exc()
            return

        self._log("Applying changes...")
        self._reader.parse(self._config_path, dt_settings.fileencoding)
        self._apply_general_section()
        self._update_event.set()

    def _update_renderer_and_execution_manager(self) -> None:
        self._log("Updating Renderer and Execution Manager...")
        events = []
        execution_events = []
        t1 = datetime.datetime.now().replace(hour=0, minute=0, second=0)
        t2 = t1 + datetime.timedelta(days=self._renderer_preview_timespan)
        for recurring_event in self._reader.recurring:
            events = events + recurring_event.get_next_simpleevents(t1, t2)
        for unique_event in self._reader.unique:
            events = events + unique_event.get_next_simpleevents(t1, t2)

        self._log("-------------------------------")
        self._log("Next Events:")
        for event in events:
            self._log("At [" + str(event.time) + "]: " + event.description)
            execution_events += event.get_execution_events()

        self._log("-------------------------------")
        self._log("Next Executions:")
        for event in execution_events:
            self._log("At [" + str(event.time) + "]: " + event.executable)
        self._log("-------------------------------")

        with self._renderer.event_lock:
            self._renderer.events = events
        self._renderer.events_changed()

        with self._execution_manager.event_lock:
            self._execution_manager.events = execution_events
            self._execution_manager.events_changed.set()

    def mainloop(self) -> None:
        self._update_thread.start()
        try:
            self._renderer.mainloop()
        except KeyboardInterrupt:
            pass

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

            if self._update_event.isSet():
                self._update_renderer_and_execution_manager()
                self._update_event.clear()

            try:
                self._execution_manager.tick()
            except OSError as e:
                self._log("Couldn't execute: " + str(e))

            if datetime.date.today() > self._cleaned_date:
                self._log("Date change detected. Cleaning...")
                copyfile(self._config_path, self._config_path + ".bak")
                try:
                    self._cleaner.clean(self._config_path,
                                        dt_settings.fileencoding)
                except Exception:
                    self._log("!!! Cleaning the config file failed. Error:")
                    traceback.print_exc()

                # trigger updating the renderer:
                self._update_event.set()
                self._cleaned_date = datetime.date.today()

            sleep(dt_settings.updatethread_sleeptime_s)


# from freezegun import freeze_time
# @freeze_time("2017-02-24 12:14:55", tick=True)
def main():
    locale.setlocale(locale.LC_ALL, '')  # apply system locale

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fullscreen",
                        help="start in fullscreen mode", action="store_true")
    args = parser.parse_args()

    # defensive loop to restart if error occurs
    exited_gracefully = False
    while not exited_gracefully:
        try:
            table = DementiaTimetable(args.fullscreen)
            table.mainloop()
            exited_gracefully = True
        except Exception:
            exited_gracefully = False
            traceback.print_exc()


if __name__ == "__main__":
    main()
