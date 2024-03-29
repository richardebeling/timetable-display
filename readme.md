# Timetable Display

Non-interactive automatic display of timetables originally written to guide people suffering from dementia through
their day.

![Screenshot of the time table](/screenshot.png?raw=true "Screenshot of the time table")

## Required Libraries:
- Tkinter - `sudo apt install python3-tk`
- WatchDog - `pip3 install watchdog`

## How to run?
Just `./dt_main.py`
`-f` or `--fullscreen` is a valid parameter to directly go to fullscreen-mode after starting.
See `./dt_main.py --help`

## Hotkeys
- F / F11 - Fullscreen
- Esc / q - Exit

## Configuration
### dt_settings.py - Internal Settings
- Configuration file path: `filepath`. Default: `config.cfg`
- Configuration file encoding: `fileencoding`. Should be `utf-8` or `latin-1` or similar.
- Update thread sleep time: `updatethread_sleeptime_s`
- Date format: dateformat: Python format string that will be formatted with `s.format(d=datetime.date())`
    Example: `{d:%A}, {d.day}. {d:%B} {d.year}`
- Clock format: clockformat: Python format string that will be formatted with `s.format(dt=datetime.datetime.now())`
    Example: `{dt.hour}:{dt.minute:02d}`

### Configuration file - User Settings
4 Sections, beginning at the markers (`[general]`, `[recurring]`, `[unique]` or `[footnotes]`).
Each section can occur more than once, though I hardly suggest not to do that. The cleaning mechanism will also undo
that structuring in the first cleaning run.

### Config reloading and cleaning
The program automatically reloads the configuration file when it is changed. This allows for headless updates, e.g.
when using a raspi, by replacing the configuration file with an updated one.

#### General Section
Simple .ini like settings:
`variable = value`

Whitespaces surrounding the variable or value will be stripped.

#### Possible variables:
- `uniquedateformat`: Python strptime format string, used in the unique section
- `footnotedateformat`: Python strptime format string, used in the footnotes section
- `head`: String that's displayed as header. Empty equals no header.
- `foot`: Same, for footer.
- `padhead`: Add a padding line after the header line
- `padfoot`: Add a padding line before the footer line. Note that the footer will always stick to the bottom of the
    screen, even without the line, so this shouldn't be necessary.
- `today`: String, text before all events that happen today.
    Can contain `$date$`, which will be replaced by the current date.
- `tomorrow`: Same as today, `$date$` will be replaced by the next day's date.
- `tomorrowbeforeevent`: Bool, if set, the tomorrow text will not be in a seperate line but before the first event on
    the next day.
- `untiltext`: Text to render when the "until" modifier is set for an event.
- `todaycount`: Number of events to display for the current day.
- `tomorrowcount`: Number of events to display for the next day.
- `pastcount`: Number of events that have passed to display before the current event for the current day.
- `hilightafter`: Time in minutes that every event will stay hilighted after it passed.
- `font`: String
- `fontsize`: Number
- `fontbold`: Bool (1/0)
- `fontitalics`: Bool (1/0)
- `fontunderlined`: Bool (1/0)
- `paddingsize`: Font size that specifies how big one padding line is.
- `bg`: background color, `white/red/gray` or `#012345`
- `fb`: foreground color
- `hbg`: background color for a hilighted event
- `hfg`: foreground color for a hilighted event
- `pbg`: background color for an event in the past
- `pfg`: foreground color for an event in the past
- `arrow`: String, file name of an image (png) that will be rendered if the `arrow` modifier is set for an event
- `showclock`: Bool, the program will show a clock ((h)h:mm) in the upper right corner
- `hideuntilwhendone`: Bool, the "until" keyboard will disappear in front of past events

### Recurring section
Events that are recurring in a two-week-period or more often.  Each event consists of two or three lines, depending on
whether the `exec` modifier is set.

The first linie specifies the times when this event happens. It consists of the time of the day followed by the days
where it happens. Possible day modifiers are `e`/`g` and `o`/`u` for even and odd weeks.

Example: `8:00 e1 o2 10:00 o1 e2`

This event happens at 8:00 Mondays on even weeks, 8:00 Tuesdays on odd weeks, 10:00 Mondays on odd weeks, Tuesdays on
even weeks.

Also, you can append modifiers to the first line. Valid modifiers are:
- `notime`: Don't render the time for this event
- `until`: Render the "untiltext" on the left side of the time
- `tomorrow`: This event will be shown in the tomorrow preview
- `padding`: This event marks a padding line
- `nodraw`: This event will not be rendered. Useful in combination with exec.
- `exec`: This event has an execution line. See below for more detail.
- `noremove`: This event will not be removed from the past events that are shown.

The second line contains the event description that will be rendered.  For padding events, a dummy text is still needed.

A third line (execution line) is only legal if the `exec` modifier is set. It consist of offsets to the event's time(s)
plus the strings that should be executed at that time.

Example: `+0 ./script.sh param1 paramt2 -5 ./another.sh test`

### Unique section
Events that are unique or reoccur less often than once per two weeks or unperiodically. Each event consists of two or
three lines, depending on whether the `exec` modifier is set.

The first line gives the timestamps when these events happen.  More than one timestamp can be given, seperated by
spaces. Thus, the `uniquedateformat` setting should not contain spaces.

The second line gives the event descriptions just like in the recurring secion.

All modifiers from the recurring section are also valid here. A third line might exist when the `exec` modifier is set.

### Foonotes section
Days where the footnote text should be replaced. This is useful for e.g. reminding of birthdays.
For the whole day, the program will not display the `foot` text from the general section but the text for the event on
this day.

Again, the first line contains a timestamp and possible modifiers. If `exec` is set, the execution will take place at
the start of the day. The execution behaviour is not tested as I don't see a use case currently, so it could be buggy.
The format for the timestamp should be set in the general section as value of `footnotedateformat`. The default is
`%d.%m` which equals DD.MM (01.10)

The second line gives the text that will be displayed on this day.
