#!/bin/python3

# dementia timetable class test file.

from shutil import copyfile
import os
import filecmp

import dt_config

reader = dt_config.ConfigReader()
reader.parse("example.cfg")

writer = dt_config.ConfigWriter()
writer.write("test.cfg", reader.general, reader.recurring, reader.unique)

copyfile("example.cfg", "test2.cfg")
cleaner = dt_config.ConfigCleaner()
cleaner.clean("test2.cfg")

if filecmp.cmp("test.cfg", "test2.cfg"):
    print("ConfigCleaner did not change anything")
    os.remove("test2.cfg")
else:
    print("ConfigCleaner changed something from test1 to test2.cfg")

if filecmp.cmp("example.cfg", "test.cfg"):
    print("ConfigWriter wrote what was in example.cfg")
    os.remove("test.cfg")
else:
    print("mismatch: example.cfg -> test.cfg")

