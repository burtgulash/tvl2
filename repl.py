#!/usr/bin/env python3

import sys
import readline
import atexit
import traceback

from ex import *


if __name__ == "__main__":
    if len(sys.argv) > 1:
        histfile = sys.argv[1]
        try:
            readline.read_history_file(histfile)
            readline.set_history_length(1000)
        except FileNotFoundError:
            pass
        atexit.register(readline.write_history_file, histfile)


    readline.parse_and_bind("set editing-mode vi")
    try:
        while True:
            x = input("    ")

            try:
                x = Parse(x)
                #print("  PARSED:", pp(x))

                x = ex(ENV, x)
                print(pp(x))
            except Exception as err:
                traceback.print_exc(file=sys.stderr)
                print("ERROR", err)
    except (KeyboardInterrupt, EOFError):
        pass
