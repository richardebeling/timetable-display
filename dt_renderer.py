#!/usr/bin/python3

import tkinter
import threading
import datetime


class TableRenderer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.events = []  # RenderEvent
        self.event_lock = threading.Lock()

        self._today_labels = []  # tkinter.label
        self._tomorrow_labels = []  # tkinter.label

        self._tk = tkinter.Tk()

        self._head_label_text = tkinter.StringVar(self._tk)
        self._foot_label_text = tkinter.StringVar(self._tk)

    def _delete_window_callback(self):
        self._tk.quit()

    def _events_changed_callback(self):
        self._handle_new_events()

    def _sort_events(self):
        self.event_lock.acquire()
        self.events = sorted(self.events, key='time')
        self.event_lock.release()

    def _clean_events(self):
        now = datetime.datetime.now()
        for event in self.events:
            if event.time < now:
                self.events.remove(event)

    def _handle_new_events(self):
        for label in self._today_labels:
            label.destroy()
        for label in self._tomorrow_labels:
            label.destroy()

        self._sort_events()
        self._clean_events()

        self._fill_window()

        #  todo
        #  Set timer to change the rendering when the time of the next event is
        #  reached.

    def set_header_text(self, s: str) -> None:
        self._head_label_text.set(s)

    def set_footer_text(self, s: str) -> None:
        self._foot_label_text.set(s)

    def mainloop(self):
        self._handle_new_events()
        self._tk.mainloop()

    def _fill_window(self):
        today_events = []
        today_limit = datetime.datetime.now()
        today_limit.replace(hour=23, minute=59, second=59)

        tomorrow_events = []
        tomorrow_limit = today_limit + datetime.timedelta(days=1)

        self.event_lock.acquire()
        for event in self.events:
            if (event.time < today_limit
                    and len(today_events) < self.count_today):
                today_events.append(event)
            elif (event.time < tomorrow_limit
                  and len(tomorrow_events) < self.count_tomorrow):
                tomorrow_events.append(event)
            elif event.time > tomorrow_limit:
                break
        self.event_lock.release()

        self._head_label = tkinter.Label(self._tk,
                                         textvariable=self._head_label_text)
        self._foot_label = tkinter.Label(self._tk,
                                         textvariable=self._foot_label_text)

        self._head_label.pack(fill=tkinter.X)

        for event in today_events:
            label = tkinter.label(self._tk, text=event.description)
            label.pack(fill=tkinter.X)
            self._today_labels.append(label)

        for event in tomorrow_events:
            label = tkinter.label(self._tk, text=event.description)
            label.pack(fill=tkinter.X)
            self._tomorrow_labels.append(label)

        self._foot_label.pack(fill=tkinter.X)

        # todo: Create labels for the next n events withing the next m days
