# cli.py - main user interface
# Copyright (C) 2024 Jonas Tingeborn

import argparse
import sys
from functools import partial

from .memory import (summarize_process_memory, show_process_tree, output_formatter,
                     row_printer, size_formatter, Unit)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Shows memory usage information for process trees'
    )

    def common(p):
        p.add_argument('-b', action='store_true', help='memory size in bytes')
        p.add_argument('-k', action='store_true', help='memory size in kilobytes')
        p.add_argument('-g', action='store_true', help='memory size in gigabytes')

    sp = parser.add_subparsers(dest='cmd', metavar='')
    tree = sp.add_parser('tree', help="display memory use for the system's process tree")
    tree.add_argument('-c', '--commands', action='store_true', help='show command line arguments for each process')
    common(tree)

    top = sp.add_parser('top', help='show process names consuming most memory (aggregates by process name)')
    top.add_argument('-n', type=int, metavar='N', default=10,
                     help='top N memory hogs (default: 10)')
    common(top)

    if len(sys.argv) < 2:
        sys.argv.append('-h')
    return parser.parse_args()


def main():
    opts = parse_args()

    unit = Unit.GB if opts.g else Unit.KB if opts.k else Unit.B if opts.b else Unit.MB
    format_size = partial(size_formatter, unit=unit)

    if opts.cmd == 'top':
        format = partial(output_formatter, show_proc=False, show_commands=False)
        summarize_process_memory(
            format_size=format_size,
            format=format,
            print_row=partial(row_printer, format_size=format_size, show_commands=False),
            sortby_size=bool(opts.n),
            max_rows=opts.n,
            reverse=True
        )
    else:
        format = partial(output_formatter, show_proc=True, show_commands=opts.commands)
        show_process_tree(
            format_size=format_size,
            format=format,
            print_row=partial(row_printer, format_size=format_size, show_commands=opts.commands),
            show_commands=opts.commands
        )


if __name__ == '__main__':
    main()
