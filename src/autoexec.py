#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import subprocess
import sys

if __name__ == '__main__':

    arg0 = sys.argv[0]

    if arg0 and arg0.isdigit():
        sec = int(arg0)
        if sec > 5:
            time_sleep = sec
        else:
            time_sleep = 30
    else:
        time_sleep = 30

    while True:
        p = subprocess.Popen(["python", "main_shiritori.py"],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout_data, stderr_data = p.communicate()
        print(stdout_data.decode('utf-8'), end="")
        sys.stdout.flush()

        time.sleep(time_sleep)
