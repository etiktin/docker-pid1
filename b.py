#!/usr/bin/env python3
import subprocess
import time

print('b.py started')
print('b.py executing c.py')
subprocess.Popen(['./c.py'])
print('b.py sleeping for 10 seconds')
time.sleep(10)
print('b.py exiting')
