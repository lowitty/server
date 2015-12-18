# encoding = utf-8

"""
@author: Yannik Wang(EJLNOQC)
@version: 2015-12-17
"""

import logging
import os
import time
import random
import sys
import threading
from datetime import datetime, timedelta


class nelogthread(threading.Thread):

    def __init__(self, ne_type, interval):
        threading.Thread.__init__(self)
        self.stopped = False
        self.ne_type = ne_type
        self.interval = interval


    def run(self):
        while not self.stopped:
            pass

    def stop(self):
        self.stopped = True

    def raw_logs(self):
        pass