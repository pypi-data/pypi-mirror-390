# memory.py - domain functions for the program
# Copyright (C) 2024 Jonas Tingeborn

from typing import Callable, Tuple, Dict, Optional
from enum import Enum
import sys

from .process import get_processes

LenMap = Dict[str, int]
PrintRow = Callable[[str, int, int, int, str, str, bool, int], None]
FormatSize = Callable[[int], str]
FormatOutput = Callable[[LenMap], Tuple[str, str]]

class Unit(Enum):
    B = 1
    KB = 2
    MB = 3
    GB = 4


def summarize_process_memory(format_size:FormatSize, format:FormatOutput, print_row:PrintRow,
                             sortby_size:bool = False, max_rows:Optional[int] = None, reverse:bool = False):
    processes = get_processes()
    names = sorted(list(set(p['name'] for p in processes.values())))
    retained = {}  # type: ignore [var-annotated]

    # Collapse memory use of all processes having the same name
    for p in processes.values():
        name = p['name']
        if name in retained:
            retained[name]['bytes'] += p['bytes']
        else:
            retained[name] = p

    # Optional sorting by size, ascending
    if sortby_size:
        names = sorted(retained, key=lambda name: retained[name]['bytes'])

    # Optional limit on number of rows to show
    limit = min(len(names), max_rows) if max_rows is not None else len(names)

    # Optional reversing of result
    if reverse:
        names = list(reversed(names))

    # Derive column formatting
    lens = get_format_lengths(format_size, processes)
    fmt, header = format(lens)

    print(header, file=sys.stderr)
    for name in names[:limit]:
        p = retained[name]
        print_row(fmt, p['pid'], p['bytes'], -1, p['name'], '', True, 0)


def get_format_lengths(format_size:FormatSize, processes: Dict[int, Dict]) -> Dict[str, int]:
    max_pid, max_procmem, totalmem, max_procname = 0, 0, 0, 0
    for p in processes.values():
        max_pid = max(max_pid, p['pid'])
        max_procmem = max(max_procmem, p['bytes'])
        totalmem += p['bytes']
        max_procname = max(max_procname, len(p['name']))

    return {
        'pid': len(str(max_pid)),
        'procname': max_procname,
        'procmem': len(format_size(max_procmem)),
        'totalmem': len(format_size(totalmem)),
    }


def show_process_tree(format_size:FormatSize, format:FormatOutput, print_row:PrintRow, show_commands:bool):
    processes = get_processes(with_cmd=show_commands)

    # Identify top/root processes to traverse from
    roots = sorted(p['pid'] for p in processes.values() if p['ppid'] is None or p['ppid'] == p['pid'])

    # Helper to find max depth and widest process name in the process tree(s)
    def dfs(pid, level=0, seen=None):
        if seen is None:
            seen = set()
        if pid not in seen:
            seen.add(pid)
            p = processes[pid]
            yield pid, level, len(p['name'])
            for cpid in p['children']:
                yield from dfs(cpid, level+1, seen)

    # Derive column formatting
    lens = get_format_lengths(format_size, processes)
    fmt, header = format(lens)

    # Print the header, then each tree in a DFS manner, starting from each process root in PID order
    print(header, file=sys.stderr)
    for root_pid in roots:
        for pid, level, _ in dfs(root_pid):
            p = processes[pid]
            print_row(fmt, pid, p['bytes'], cummulative_bytes(processes, pid),
                      p['name'], p['cmd'], False, level)


def cummulative_bytes(processes, pid):
    process = processes[pid]
    total = process['bytes']
    for cpid in process['children']:
        total += cummulative_bytes(processes, cpid)
    return total


def row_printer(fmt:str, pid:int, bytes:int, totbytes:int, name:str, cmd:str, only_total:bool, indent:int,
                format_size:FormatSize, show_commands:bool):
    tot = '' if totbytes < 0 or totbytes == bytes else format_size(totbytes)
    pad = ' '
    if only_total:
        print(fmt % (str(pid), format_size(bytes), (pad*(indent*2)) + name))
    else:
        vals = [str(pid), tot, format_size(bytes), (pad*(indent*2)) + name]
        if show_commands:
            vals.append(cmd)
        print(fmt % tuple(vals))


def output_formatter(len_map:Dict[str, int], show_proc:bool, show_commands:bool) -> Tuple[str, str]:
    headers = ['PID', 'Aggregate', 'Memory', 'Process']
    mpid, mtot, mmem, mname = [max(len_map[k], len(header)) for k, header
                               in zip(('pid', 'totalmem', 'procmem', 'procname'), headers)]

    cols = [
        ('PID', f'%{mpid}s', '-'*mpid),
        ('Aggregate', f'%{mtot}s', '-'*mtot),
        ('Memory', f'%{mmem}s', '-'*mmem),
        ('Process', f'%-{mname}s', '-'*mname),
        ('Command', '%s', '-'*20),
    ]
    if not show_proc:
        cols = [x for x in cols if x[0] != 'Memory']
    if not show_commands:
        cols = [x for x in cols if x[0] != 'Command']

    names = [x[0] for x in cols]
    fmt = '  '.join(x[1] for x in cols)
    dashes = [x[2] for x in cols]
    header = '\n'.join(fmt % tuple(x) for x in (names, dashes))
    return fmt, header

def size_formatter(n:int, unit:Unit) -> str:
    if unit == Unit.MB:
        return '%.0d MB' % (n/(1 << 20))
    elif unit == Unit.GB:
        return '%.0d GB' % (n/(1 << 30))
    elif unit == Unit.KB:
        return '%.0d KB' % (n/(1 << 10))
    else:  # bytes
        return str(n)
