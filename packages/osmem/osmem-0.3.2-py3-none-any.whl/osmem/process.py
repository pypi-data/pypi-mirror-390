# process.py - process information extraction
# Copyright (C) 2024 Jonas Tingeborn

from typing import Dict
import psutil  # type: ignore [import]

from .windows import get_pid_map  # is None on non-windows platforms

def get_processes(with_cmd=False) -> Dict[int, Dict]:
    pids = None
    if get_pid_map is not None:   # windows accelerated ppid lookup
        pids = get_pid_map()

        def get_ppid(p):
            return pids.get(p.pid)
    else:
        def get_ppid(p):
            return p.ppid()

    processes = {}
    for p in psutil.process_iter():
        mem = p.memory_info()
        # windows (task mgr) uses private bytes, wereas *nix relies on rss
        b = mem.private if hasattr(mem, 'private') else mem.rss
        exe = get(p, 'exe')
        args = (get(p, 'cmdline') or []) if with_cmd else []  # type: ignore [var-annotated]
        processes[p.pid] = {
            'pid': p.pid,
            'ppid': get_ppid(p),
            'name': p.name(),
            'bytes': b,
            'exe': exe,
            'children': [],
            'cmd': ' '.join(quote(s) for s in args),
            'created': p.create_time(),
        }

    for p in processes.values():
        pid, ppid = p['pid'], p['ppid']
        if valid_parent(processes, pid, ppid):
            parent = processes[ppid]
            parent['children'].append(pid)
        else:
            p['ppid'] = None

    return processes


def get(p, what):
    try:
        return getattr(p, what)()
    except psutil.AccessDenied:
        return None

def quote(s):
    return f'"{s}"' if ' ' in s else s

def valid_parent(processes, pid, ppid):
    if (pid is None or ppid is None) or pid == ppid or ppid not in processes:
        return False
    # Filter out stale ppid references (children still referencing dead parents, which have
    # been replaced by new processes reusing the same pids!)
    return processes[ppid]['created'] < processes[pid]['created']
