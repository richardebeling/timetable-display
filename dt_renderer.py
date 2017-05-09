#!/usr/bin/python3

from dt_event import SimpleEvent
from typing import List
import tkinter
import threading
import datetime


class TableRenderer():
    _col_arrow = 0
    _col_time = 1
    _col_text = 2
    _col_clock = 3
    _col_count = 4

    def __init__(self, fullscreen):
        # todo: Lock for all these settings?
        self.count_today = 5
        self.count_tomorrow = 2
        self.hilight_after = 10                   # minutes
        self.show_clock = True
        self.hide_until_when_done = False
        self.keep_past_events_from_today = True

        self.font = {'name': "Arial", 'size': 30, 'bold': False,
                     'italics': False, 'underlined': False, 'paddingsize': 30}
        self._font_string = "Arial 30"

        self.texts = {'head': "", 'foot': "", 'tomorrow': "$date$",
                      'today': "$date$", 'until': "until"}
        self.colors = {'fg': "black", 'bg': "white", 'hfg': "yellow",
                       'hbg': "blue", 'pbg': "black", 'pfg': "grey"}

        self.events = []                          # SimpleEvent
        self.event_lock = threading.Lock()

        self._labels = []
        # List of lists: [3 x None or tkinter.Label], arrow, time and text

        self._arrow = None                        # Tkinter.PhotoImage
        self._fullscreen_state = False

        self._tk = tkinter.Tk()
        self._tk.wm_title("Dementia Timetable")
        self._tk.focus_set()
        self._tk.bind('f', self._toggle_fullscreen_event_handler)
        self._tk.bind('q', lambda e: self._tk.quit())
        self._tk.bind('<F11>', self._toggle_fullscreen_event_handler)
        self._tk.bind('<Escape>', lambda e: self._tk.quit())
        self._clock_text = tkinter.StringVar()
        self._update_clock_text()
        self._tk.grid_columnconfigure(self._col_clock, weight=1)

        if fullscreen:
            self._toggle_fullscreen()

        # in order to detect and raise a keyboard interrupt, tkinter has to be
        # active -> generate activity:
        self._dummy_activity()

    def _update_clock_text(self):
        text = "{dt.hour}:{dt.minute:02d}".format(dt=datetime.datetime.now())
        self._clock_text.set(text)
        self._tk.after(1000, self._update_clock_text)

    def _dummy_activity(self):
        self._tk.after(100, self._dummy_activity)

    def _delete_window_callback(self) -> None:
        self._tk.quit()

    def _toggle_fullscreen_event_handler(self, event):
        self._toggle_fullscreen()

    def _toggle_fullscreen(self):
        self._fullscreen_state = not self._fullscreen_state
        self._tk.attributes('-fullscreen', self._fullscreen_state)
        cursor = "none" if self._fullscreen_state else "arrow"
        self._tk.config(cursor=cursor)

    def _sort_events(self) -> None:
        with self.event_lock:
            self.events = sorted(self.events, key=lambda event: event.time)

    def _remove_past_events(self) -> None:
        with self.event_lock:
            now = datetime.datetime.now()
            now = now - datetime.timedelta(minutes=self.hilight_after)
            today_morning = datetime.datetime.now().replace(hour=0, minute=0)
            if self.keep_past_events_from_today:
                for event in self.events:
                    if event.time < today_morning:
                        self.events.remove(event)
            else:
                for event in self.events:
                    if event.time < now:
                        self.events.remove(event)

    def _remove_nodraw_events(self) -> None:
        with self.event_lock:
            for event in self.events:
                if "nodraw" in event.modifiers:
                    self.events.remove(event)

    def _handle_new_events(self) -> None:
        self._sort_events()
        self._remove_past_events()
        self._remove_nodraw_events()

        today_events, tomorrow_events = self._get_events_to_render()
        hilight_event = self._find_event_to_hilight(today_events)
        self._tk.configure(bg=self.colors['bg'])

        self._clear_window()
        self._fill_window(today_events, tomorrow_events, hilight_event,
                          datetime.datetime.now())

        if hilight_event is None:
            t = datetime.datetime.today().replace(hour=0, minute=0, second=0)
            t = t + datetime.timedelta(days=1)
        else:
            t = hilight_event.time
            t = t + datetime.timedelta(minutes=self.hilight_after)

        self._handle_new_events_set_timer(t)

    def _handle_new_events_set_timer(self, when: datetime.datetime) -> None:
        timediff = when - datetime.datetime.now()
        time = timediff.total_seconds() * 1000

        time = 1000 * 10 if time < 0 else time
        self._tk.after(int(time), self._handle_new_events)

    def _prepare_today_text(self) -> str:
        date = datetime.date.today()
        datestr = "{d.day}. {d:%B} {d.year}".format(d=date)
        return self.texts['today'].replace("$date$", datestr)

    def _prepare_tomorrow_text(self) -> str:
        date = datetime.date.today() + datetime.timedelta(days=1)
        datestr = "{d.day}. {d:%B} {d.year}".format(d=date)
        return self.texts['tomorrow'].replace("$date$", datestr)

    def _build_font_string(self) -> None:
        result = self.font['name'] + " " + str(self.font['size'])
        if self.font['bold'] is not False:
            result += " bold"
        if self.font['italics'] is not False:
            result += " italic"
        if self.font['underlined'] is not False:
            result += " underlined"
        self._font_string = result

    def _get_normal_label(self, text) -> tkinter.Label:
        label = tkinter.Label(self._tk, text=text)
        label.config(bg=self.colors['bg'], fg=self.colors['fg'])
        label.config(font=self._font_string)
        return label

    def _get_stringvar_label(self, stringvar) -> tkinter.Label:
        label = tkinter.Label(self._tk, textvariable=stringvar)
        label.config(bg=self.colors['bg'], fg=self.colors['fg'])
        label.config(font=self._font_string)
        return label

    def _get_padding_label(self) -> tkinter.Label:
        pad_font = self._font_string.replace(
            str(self.font['size']), str(self.font['paddingsize']))
        label = tkinter.Label(self._tk, text="A")
        label.config(bg=self.colors['bg'], fg=self.colors['bg'])
        label.config(font=pad_font)
        return label

    def _get_past_label(self, text) -> tkinter.Label:
        label = tkinter.Label(self._tk, text=text)
        label.config(bg=self.colors['pbg'], fg=self.colors['pfg'])
        label.config(font=self._font_string)
        return label

    def _get_hilight_label(self, text) -> tkinter.Label:
        label = tkinter.Label(self._tk, text=text)
        label.config(bg=self.colors['hbg'], fg=self.colors['hfg'])
        label.config(font=self._font_string)
        return label

    def _create_head_line_with_clock(self, text: str, row: int) -> None:
        label = self._get_normal_label(text)
        label.configure(anchor=tkinter.W)
        label.grid(columnspan=self._col_count-self._col_arrow-1,
                   column=self._col_arrow, row=row, sticky="NSWE")
        label_clock = self._get_stringvar_label(self._clock_text)
        label_clock.configure(anchor=tkinter.E)
        label_clock.grid(column=self._col_clock, row=row, sticky="NSWE")
        self._labels.append([None, label, None, label_clock])

    def _create_head_line(self, text: str, row: int) -> None:
        label = self._get_normal_label(text)
        label.configure(anchor=tkinter.W)
        label.grid(columnspan=self._col_count, column=self._col_arrow, row=row,
                   sticky="NSWE")
        self._labels.append([label, None, None, None])

    def _create_normal_event_line(self, event: SimpleEvent, row: int) -> None:
        return self._create_event_line(event, row, self._get_normal_label)

    def _create_past_event_line(self, event: SimpleEvent, row: int) -> None:
        return self._create_event_line(event, row, self._get_past_label, False)

    def _create_event_line(self, event: SimpleEvent, row: int,
                           get_label_func: callable, until=True) -> None:
        ls = []

        if until:
            condition_until = "until" in event.modifiers
            text = self.texts['untiltext'] + " " if condition_until else ""
            label_until = get_label_func(text)
            label_until.configure(anchor=tkinter.E)
            label_until.grid(column=self._col_arrow, row=row, sticky="NSWE")
            ls.append(label_until)
        else:
            ls.append(None)

        condition_time = "notime" not in event.modifiers
        text = event.timestring() + " " if condition_time else ""
        label_time = get_label_func(text)
        label_time.configure(anchor=tkinter.E)
        label_time.grid(column=self._col_time, row=row, sticky="NSWE")
        ls.append(label_time)

        label_text = get_label_func(event.description)
        label_text.configure(anchor=tkinter.W)
        label_text.grid(column=self._col_text, columnspan=self._col_count,
                        row=row, sticky="NSWE")
        ls.append(label_text)

        ls.append(None)

        self._labels.append(ls)

    def _create_hilight_event_line(self, event: SimpleEvent, row: int) -> None:
        ls = []

        if "until" not in event.modifiers and self._arrow is not None:
            label_until = tkinter.Label(self._tk, image=self._arrow)
            label_until.configure(bg=self.colors['hbg'], fg=self.colors['hfg'])
        else:
            condition_until = "until" in event.modifiers
            text = self.texts['untiltext'] + " " if condition_until else ""
            label_until = self._get_hilight_label(text)
        label_until.configure(anchor=tkinter.E)
        label_until.grid(column=self._col_arrow, row=row, sticky="NSWE")
        ls.append(label_until)

        condition_time = "notime" not in event.modifiers
        text = event.timestring() + " " if condition_time else ""
        label_time = self._get_hilight_label(text)
        label_time.configure(anchor=tkinter.E)
        label_time.grid(column=self._col_time, row=row, sticky="NSWE")
        ls.append(label_time)

        label_text = self._get_hilight_label(event.description)
        label_text.configure(anchor=tkinter.W)
        label_text.grid(column=self._col_text,
                        columnspan=self._col_count-self._col_text, row=row,
                        sticky="NSWE")
        ls.append(label_text)

        ls.append(None)

        self._labels.append(ls)

    def _create_padding_line(self, row: int, past: bool = False) -> None:
        label = self._get_padding_label()
        if past:
            label.configure(bg=self.colors['pbg'], fg=self.colors['pbg'])
        else:
            label.configure(bg=self.colors['bg'], fg=self.colors['bg'])
        label.grid(column=self._col_arrow, columnspan=self._col_count,
                   row=row, sticky="NSWE")
        self._labels.append([None, None, label, None])

    def _get_events_to_render(self) -> List[SimpleEvent]:
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
                      and len(tomorrow_events) < self.count_tomorrow
                      and "tomorrow" in event.modifiers):
                    tomorrow_events.append(event)
                elif event.time > tomorrow_limit:
                    break

        return today_events, tomorrow_events

    def _find_event_to_hilight(self, events: List[SimpleEvent]) -> SimpleEvent:
        hilight_event = None
        limit = datetime.datetime.now()
        limit = limit - datetime.timedelta(minutes=self.hilight_after)
        for event in events:
            if (limit < event.time
                    and hilight_event is None
                    and "padding" not in event.modifiers):
                hilight_event = event
        return hilight_event

    def _clear_window(self) -> None:
        for line in self._labels:
            for element in line:
                if element is not None:
                    element.grid_forget()
                    element.destroy()
        self._labels = []

    def _fill_window(self,
                     today_events: List[SimpleEvent],
                     tomorrow_events: List[SimpleEvent],
                     hilight_event: SimpleEvent,  # or None
                     current_time: datetime.datetime) -> None:
        self._build_font_string()
        event_drawn = False
        row = 0

        if len(self.texts['head']) != 0:
            row = row + 1
            self._create_padding_line(row)
            row = row + 1

        if (len(self.texts['today']) != 0 and len(today_events) > 0
                or self.show_clock):
            event_drawn = True
            if self.show_clock:
                self._create_head_line_with_clock(self._prepare_today_text(),
                                                  row)
            else:
                self._create_head_line(self._prepare_today_text(), row)
            row = row + 1

        for event in today_events:
            event_drawn = True
            if "padding" in event.modifiers:
                self._create_padding_line(row)
            elif event == hilight_event:
                self._create_hilight_event_line(event, row)
            elif event.time < current_time:
                self._create_past_event_line(event, row)
            else:
                self._create_normal_event_line(event, row)
            row = row + 1

        if event_drawn:
            self._create_padding_line(row)
            row = row + 1

        if len(self.texts['tomorrow']) != 0 and len(tomorrow_events) > 0:
            self._create_head_line(self._prepare_tomorrow_text(), row)
            row = row + 1

        for event in tomorrow_events:
            if "padding" in event.modifiers:
                self._create_padding_line(row)
            else:
                self._create_normal_event_line(event, row)
            row = row + 1

        if len(self.texts['foot']) != 0:
            self._create_head_line(self.texts['foot'], row)
            row = row + 1

        return hilight_event

    def mainloop(self) -> None:
        self._handle_new_events()
        self._tk.mainloop()

    def events_changed(self) -> None:
        self._tk.after(0, self._handle_new_events)

    def load_arrow_image(self, path) -> None:
        self._arrow = tkinter.PhotoImage(file=path)
