#!/usr/bin/python3

import Tkinter
import threading


class TableRenderer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()

        self.events = []
        self.event_lock = threading.Lock()

    def _delete_window_callback(self):
        self.root.quit()

    def _events_changed_callback(self):
        self._handle_new_events()

    def _handle_new_events(self):
        print("nothing")
        #  todo
        #  Delete everything that is drawn
        #  Sort events
        #  Draw N events, hilighting the current
        #  Set timer to change the rendering when the time of the next event is
        #  reached.

    def run(self):
        self._tk = Tkinter.Tk()
        self._tk.protocol("WM_DELETE_WINDOW", self._delete_window_callback)

        self._fill_window()

        self._tk.mainloop()

    def _fill_window():
        # todo
        print("nothing")
