# -*- coding: utf-8 -*-
import random
import time

def retry_call(f, random_time, max_retry=3):
    for _ in range(max_retry):
        try:
            return f()
        except:
            time.sleep(random.randint(0, random_time))
    return f()
