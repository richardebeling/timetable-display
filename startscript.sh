#!/bin/bash
# Example rc.local entry:
# (/bin/sleep 30 && cd /home/pi/dementia-timetable && exec su pi -c './startscript.sh')
#

echo "Making sure the desktop environment is running..."
service lightdm status &> /dev/null
if [ $? -ne 0 ]; then
    echo "! Seems like lightdm is not running !"
    exit
fi


_SNAME=dt
tmux has-session -t dt &> /dev/null
if [ $? -eq 0 ]; then
    echo "! Seems like the program is already running !"
    exit
fi

echo "Starting dementia timetable in a new tmux session..."
tmux new-session -s $_SNAME -x 140 -y 35 -d
tmux send-keys 'DISPLAY=:0 LANG=de_DE.utf8 ./dt_main.py -f' Enter

