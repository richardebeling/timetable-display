#!/usr/bin/python3

import tkinter
import threading
import datetime


class TableRenderer():
    def __init__(self):
        self.count_today = 5
        self.count_tomorrow = 2

        self.events = []  # RenderEvent from dt_event.py
        self.event_lock = threading.Lock()

        self._today_labels = []  # tkinter.Label
        self._tomorrow_labels = []  # tkinter.Label

        self._tk = tkinter.Tk()

        self._head_label_text = tkinter.StringVar(self._tk)
        self._foot_label_text = tkinter.StringVar(self._tk)
        self._head_label = tkinter.Label(self._tk,
                                         textvariable=self._head_label_text)
        self._foot_label = tkinter.Label(self._tk,
                                         textvariable=self._foot_label_text)

    def _delete_window_callback(self) -> None:
        self._tk.quit()

    def _sort_events(self) -> None:
        with self.event_lock:
            self.events = sorted(self.events, key=lambda event: event.time)

    def _clean_events(self) -> None:
        with self.event_lock:
            now = datetime.datetime.now()
            for event in self.events:
                if event.time < now:
                    self.events.remove(event)

    def _handle_new_events(self) -> None:
        for label in self._today_labels:
            label.destroy()
        for label in self._tomorrow_labels:
            label.destroy()

        self._sort_events()
        self._clean_events()

        self._fill_window()

        self._handle_new_events_set_timer()

    def _handle_new_events_set_timer(self) -> None:
        time = 10*1000
        with self.event_lock:
            # events should be sorted here, so the first event is the next one.
            if len(self.events) == 0:
                return
            delta = self.events[0].time - datetime.datetime.now()
            time = 1000 * delta.total_seconds() + 1

        time = 1000 if time < 0 else time  # force at least 1 second pause
        self._tk.after(int(time), self._handle_new_events)

    def events_changed(self) -> None:
        self._tk.after(0, self._handle_new_events)

    def set_header_text(self, s: str) -> None:
        self._head_label_text.set(s)

    def set_footer_text(self, s: str) -> None:
        self._foot_label_text.set(s)

    def mainloop(self) -> None:
        self._handle_new_events()
        self._tk.mainloop()

    def _fill_window(self) -> None:
        today_events = []
        today_limit = datetime.datetime.now()
        today_limit.replace(hour=23, minute=59, second=59)

        tomorrow_events = []
        tomorrow_limit = today_limit + datetime.timedelta(days=1)

        with self.event_lock:
            for event in self.events:
                if (event.time < today_limit
                        and len(today_events) < self.count_today):
                    today_events.append(event)
                elif (event.time < tomorrow_limit
                      and len(tomorrow_events) < self.count_tomorrow):
                    tomorrow_events.append(event)
                elif event.time > tomorrow_limit:
                    break

        self._head_label.pack_forget()
        self._foot_label.pack_forget()
        for label in self._today_labels:
            label.destroy()
        for label in self._tomorrow_labels:
            label.destroy()

        self._head_label.pack(fill=tkinter.X)

        for event in today_events:
            label = tkinter.Label(self._tk, text=event.description)
            label.pack(fill=tkinter.X)
            self._today_labels.append(label)

        for event in tomorrow_events:
            label = tkinter.Label(self._tk, text=event.description)
            label.pack(fill=tkinter.X)
            self._tomorrow_labels.append(label)

        self._foot_label.pack(fill=tkinter.X)
