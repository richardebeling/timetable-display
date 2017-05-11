# Dementia Timetable Readme
## Required Libraries:
- WatchDog - `sudo pip3 install watchdog`

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

### Configuration file - User Settings
3 Sections, beginning at the markers (`[general]`, `[recurring]` or `[unique]`).
Each section can occur more than once, though I hardly suggest not to do that. The cleaning mechanism will also undo that structuring in the first cleaning run.

#### General Section
Simple .ini like settings:
`variable = value`

Whitespaces surrounding the variable or value will be stripped.

#### Possible variables:
- `uniquedateformat`: Python strptime format string, used in the unique section
- `head`: String that's displayed as header. Empty equals no header.
- `foot`: Same, for footer.
- `padhead`: Add a padding line after the header line
- `padfoot`: Add a padding line before the footer line
- `today`: String, text before all events that happen today.
    Can contain `$date$`, which will be replaced by the current date.
- `tomorrow`: Same as today, `$date$` will be replaced by the next day's date.
- `untiltext`: Text to render when the "until" modifier is set for an event.
- `todaycount`: Number of events to display for the current day.
- `tomorrowcount`: Number of events to display for the next day.
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
- `arrow`: String, file name of an image (png) that will be rendered if the
    `arrow` modifier is set for an event
- `showclock`: Bool, the program will show a clock ((h)h:mm) in the upper
    right corner
- `hideuntilwhendone`: Bool, the "until" keyboard will disappear in front of
    past events

### Recurring section
Events that are recurring in a two-week-period or more often.
Each event consists of two or three lines, depending on whether the `exec` modifier is set.

The first linie specifies the times when this event happens. It consists of the
time of the day followed by the days where it happens. Possible day modifiers are
`e`/`g` and `o`/`u` for even and odd weeks.

Example: `8:00 e1 o2 10:00 o1 e2`

This event happens at 8:00 Mondays on even weeks, 8:00 Tuesdays on odd weeks,
10:00 Mondays on off weeks, Tuesdays on even weeks

Also, you can append modifiers to the first line. Valid modifiers are:
- `notime`: Don't render the time for this event
- `until`: Render the "untiltext" on the left side of the time
- `tomorrow`: This event will be shown in the tomorrow preview
- `padding`: This event marks a padding line
- `nodraw`: This event will not be rendered. Useful in combination with exec.
- `exec`: This event has an execution line. See below for more detail.

The second line contains the event description that will be rendered.
For padding events, a dummy text is still needed.

A third line (execution line) is only legal if the `exec` modifier is set. It consist of offsets to the event's time(s) plus the strings that should be executed at that time.

Example: `+0 ./script.sh param1 paramt2 -5 ./another.sh test`

### Unique section
Events that are unique or reoccur less often than once per two weeks or unperiodically.
Each event consists of two or three lines, depending on whether the `exec` modifier is set.

The first line gives the timestamps when these
events happen. More than one timestamp can be given, seperated by spaces. Thus,
the `uniquedateformat` setting should not contain spaces.

The second line gives the event descriptions just like in the recurring secion.

All modifiers from the recurring section are also valid here. A third line might exist when the `exec` modifier is set.
