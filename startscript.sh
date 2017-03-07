#!/bin/bash

echo "Making sure the desktop environment is running..."
sudo service lightdm start
echo "Starting dementia timetable..."
DISPLAY=:0 LANG=de_DE.utf8 ./dt_main.py -f

