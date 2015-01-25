#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import commands
import sys

if __name__ == '__main__':

    time_sleep = 60

    while True:
        check = commands.getoutput("python bot.py")
        print check
        sys.stdout.flush()

        time.sleep(time_sleep)
