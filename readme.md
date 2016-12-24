# Dementia Timetable Readme
## Required Libraries:
- WatchDog - `sudo pip3 install watchdog`

## Hotkeys
- F - Fullscreen
- Esc - Exit

## Configuration
- Configuration file path: specified in dt_settings.py. Default: `config.cfg`
- Update thread sleep time: specified in dt_settings.py.

### Configuration file
3 Sections, beginning at the markers (`[general]`, `[recurring]` or `[unique]`).

#### General Section
Simple .ini like settings:
`variable = value`

Whitespaces surrounding the variable or value will be stripped.

#### Possible variables:
- `uniquedateformat`: Python strptime format string, used in the unique section
- `head`: String that's displayed as header. Empty equals no header.
- `foot`: Same, for footer.
- `today`: String, text before all events that happen today.
    Can contain `$date$`, which will be replaced by the current date.
- `tomorrow`: Same as today, `$date$` will be replaced by the next day's date.
- `untiltext`: Text to render when the "until" modifier is set for an event.
- `todaycount`: Number of events to display for the current day.
- `tomorrowcount`: Number of events to display for the next day.
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

### Recurring section
Events that are recurring in a two-week-period or more often.
Each event consists of two lines.

The first linie specifies the times when this event happens. It consists of the
time of the day followed by the days where it happens. Possible day modifiers are
`e`/`g` and `o/u` for even and odd weeks.

Example: `8:00 e1 o2 10:00 o1 e2`

This event happens at 8:00 Mondays on even weeks, 8:00 Tuesdays on odd weeks,
10:00 Mondays on off weeks, Tuesdays on even weeks

Also, you can append modifiers to the first line. Valid modifiers are:
- `notime`: Don't render the time for this event
- `until`: Render the "untiltext" on the left side of the time
- `tomorrow`: This event will be shown in the tomorrow preview
- `padding`: This event marks a padding line

The second line contains the event description that will be rendered.
For padding events, a dummy text is still needed.

### Unique section
Events that are unique or reoccur less often than once per two weeks or unperiodically.
Each event consists of two lines.

The first line gives the timestamps when these
events happen. More than one timestamp can be given, seperated by spaces. Thus,
the `uniquedateformat` setting should not contain spaces.

The second line gives the event descriptions just like in the recurring secion.
