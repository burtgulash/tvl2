#!/usr/bin/env python3

import readline

from ex import *


if __name__ == "__main__":
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
                print("ERROR", err)
    except KeyboardInterrupt:
        pass
