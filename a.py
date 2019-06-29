#!/usr/bin/env python3
import subprocess
import time

import psutil
from psutil import NoSuchProcess, STATUS_ZOMBIE, ZombieProcess

# The order in which we want to print processes
ORDERED_PS_NAMES = ('init', 'a.py', 'b.py', 'c.py')


def get_ps_map():
    """Get a mapping between process name to PID"""
    current_process = psutil.Process()
    current_pid = current_process.pid
    ps_map = {'a.py': current_pid}
    if current_pid != 1:
        ps_map['init'] = 1
    for p in current_process.children(recursive=True):
        try:
            pid = p.pid
            cmd = p.cmdline()
            if './b.py' in cmd:
                ps_map['b.py'] = pid
            elif './c.py' in cmd:
                ps_map['c.py'] = pid
        except (NoSuchProcess, ZombieProcess):
            pass

    return ps_map


def is_deadish(pid):
    """Check if the process is no longer running (either a zombie or no longer exist)"""
    try:
        p = psutil.Process(pid)
        if p.status() != STATUS_ZOMBIE:
            return False
    except NoSuchProcess:
        pass

    # The process is dead-ish (either we got NoSuchProcess or it's a zombie)
    return True


def print_ps_info(ps_map):
    """Print process info for each of the processes in the provided map"""
    print('PPID', 'PID', 'STATUS', 'NAME', 'CMD', sep='\t')
    for name in ORDERED_PS_NAMES:
        if name not in ps_map:  # E.g. a.py is init
            continue

        pid = ps_map[name]
        try:
            p = psutil.Process(pid)
            ppid = p.ppid()
            cmd = ' '.join(p.cmdline()) or '-'
            status = 'zombie' if p.status() == STATUS_ZOMBIE else 'running'
            print(ppid, pid, status, name, cmd, sep='\t')
        except NoSuchProcess:
            print('-', pid, 'dead', name, '-', sep='\t')
    print('')


print('a.py started')
print('a.py executing b.py')
bpy_proc = subprocess.Popen(['./b.py'])

# Wait for all the process to start
while True:
    ps_map = get_ps_map()
    if 'c.py' in ps_map:
        break
    time.sleep(1)

print('\nStatus - all processes are running (notice the parent PIDs):')
print_ps_info(ps_map)

# Wait for b.py to die
bpy_proc.wait()
print('\nStatus - b.py is dead, so c.py was orphaned (PPID changed to 1):')
print_ps_info(ps_map)

# Wait for c.py to die
while True:
    if is_deadish(ps_map['c.py']):
        break
    time.sleep(1)

print('\nStatus - c.py is either dead or a zombie (run docker with --init to fix it):')
print_ps_info(ps_map)

print("a.py sleeping for 10 minutes (send a SIGTERM to stop me - if it " 
      "doesn't, run docker with --init and it will)")
time.sleep(600)
print('a.py exiting')
