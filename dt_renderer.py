#!/usr/bin/python3

from dt_event import RenderEvent
import tkinter
import threading
import datetime

# todo: fullscreen modus
# todo: hilight current event - changed colors + arrow
# todo: Padding events
# todo: Trennlinien - waagerecht
# todo: Hervorheben: Setzbares Interval
# todo: Ton bei Wechsel - Lautstärke anpassen nach Umgebungslautstärke
# todo: Farben anpassen nach Umgebungslicht?
# todo: Pfeilspalte + Bisspalte, Uhrzeitspalte, Textspalte


class TableRenderer():
    _col_arrow = 0
    _col_time = 1
    _col_text = 2

    def __init__(self):
        self.count_today = 5
        self.count_tomorrow = 2
        self.keep_past_events_from_today = True

        self.font = {'name': "Arial", 'size': 30, 'bold': False,
                     'italics': False, 'underlined': False}

        self.texts = {'head': "", 'foot': "", 'tomorrow': "$date$",
                      'today': "$date$", 'until': "until"}

        self.colors = {'fg': "black", 'bg': "white", 'hfg': "yellow",
                       'hbg': "blue"}

        self.events = []  # RenderEvent from dt_event.py
        self.event_lock = threading.Lock()

        self._labels = []
        # List of lists: [3 x None or tkinter.Label], arrow, time and text

        self._tk = tkinter.Tk()
        self._tk.wm_title("Dementia Timetable")

    def _delete_window_callback(self) -> None:
        self._tk.quit()

    def _sort_events(self) -> None:
        with self.event_lock:
            self.events = sorted(self.events, key=lambda event: event.time)

    def _remove_past_events(self) -> None:
        with self.event_lock:
            now = datetime.datetime.now()
            today_morning = datetime.datetime.now().replace(hour=0, minute=0)
            if self.keep_past_events_from_today:
                for event in self.events:
                    if event.time < now:
                        self.events.remove(event)
            else:
                for event in self.events:
                    if event.time < today_morning:
                        self.events.remove(event)

    def _handle_new_events(self) -> None:
        self._sort_events()
        self._remove_past_events()

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

    def _prepare_today_text(self) -> str:
        date = datetime.date.today()
        datestr = "{d.day}. {d:%B} {d.year}".format(d=date)
        return self.texts['today'].replace("$date$", datestr)

    def _prepare_tomorrow_text(self) -> str:
        date = datetime.date.today() + datetime.timedelta(days=1)
        datestr = "{d.day}. {d:%B} {d.year}".format(d=date)
        return self.texts['today'].replace("$date$", datestr)

    def _build_temp_font_string(self) -> None:
        result = self.font['name'] + " " + str(self.font['size'])
        if self.font['bold'] is not False:
            result += " bold"
        if self.font['italics'] is not False:
            result += " italic"
        if self.font['underlined'] is not False:
            result += " underlined"
        self._temp_font_string = result

    def _get_normal_label(self, text) -> tkinter.Label:
        label = tkinter.Label(self._tk, text=text)
        label.config(bg=self.colors['bg'], fg=self.colors['fg'])
        label.config(font=self._temp_font_string)
        return label

    def _get_hilight_label(self, text) -> tkinter.Label:
        label = tkinter.Label(self._tk, text=text)
        label.config(bg=self.colors['hbg'], fg=self.colors['hfg'])
        label.config(font=self._temp_font_string)

    def _create_head_line(self, text: str, row: int) -> None:
        label = self._get_normal_label(text)
        label.configure(anchor=tkinter.W)
        label.grid(columnspan=2, column=self._col_time, row=row,
                   sticky="NSWE")
        self._labels.append([None, label, None])

    def _create_event_line(self, event: RenderEvent, row: int) -> None:
        ls = []
        if "until" in event.modifiers:
            label_until = self._get_normal_label(self.texts['untiltext'] + " ")
            label_until.configure(anchor=tkinter.E)
            label_until.grid(column=self._col_arrow, row=row, sticky="NSWE")
            ls.append(label_until)
        else:
            ls.append(None)

        if "notime" not in event.modifiers:
            label_time = self._get_normal_label(event.timestring() + " ")
            label_time.configure(anchor=tkinter.E)
            label_time.grid(column=self._col_time, row=row, sticky="NSWE")
            ls.append(label_time)
        else:
            ls.append(None)

        label_text = self._get_normal_label(event.description)
        label_text.configure(anchor=tkinter.W)
        label_text.grid(column=self._col_text, row=row, sticky="NSWE")
        ls.append(label_text)

        self._labels.append(ls)

    def _fill_window(self) -> None:
        # create list of events to render
        today_events = []
        today_limit = datetime.datetime.now()
        today_limit = today_limit.replace(hour=23, minute=59, second=59)

        tomorrow_events = []
        tomorrow_limit = today_limit + datetime.timedelta(days=1)

        with self.event_lock:
            for event in self.events:
                if (event.time < today_limit
                        and len(today_events) < self.count_today):
                    today_events.append(event)
                elif (event.time > today_limit
                      and event.time < tomorrow_limit
                      and len(tomorrow_events) < self.count_tomorrow):
                    tomorrow_events.append(event)
                elif event.time > tomorrow_limit:
                    break

        # clear window
        for line in self._labels:
            for element in line:
                if element is not None:
                    element.grid_forget()
                    element.destroy()

        # fill window
        self._build_temp_font_string()
        self._tk.configure(bg=self.colors['bg'])

        row = 0

        if len(self.texts['head']) != 0:
            self._create_head_line(self.texts['head'], row)
            row = row + 1

        if len(self.texts['today']) != 0:
            self._create_head_line(self._prepare_today_text(), row)
            row = row + 1

        for event in today_events:
            self._create_event_line(event, row)
            row = row + 1

        if len(self.texts['tomorrow']) != 0:
            self._create_head_line(self._prepare_tomorrow_text(), row)
            row = row + 1

        for event in tomorrow_events:
            self._create_event_line(event, row)
            row = row + 1

        if len(self.texts['foot']) != 0:
            self._create_head_line(self.texts['foot'], row)
            row = row + 1

    def mainloop(self) -> None:
        self._handle_new_events()
        self._tk.mainloop()

    def events_changed(self) -> None:
        self._tk.after(0, self._handle_new_events)
