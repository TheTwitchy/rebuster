#!/usr/bin/env python

import sys
#An example program that evaluates simple expressions
#Takes in a single arg, which is a string to be evaluated
#Ex. math_val.py "add 1 2 3 4"

cmd = sys.argv[1]
cmd_args = cmd.split(" ")
try:
    if cmd_args[0].lower() == "add":
        result = 0
        for arg in cmd_args[1:]:
            result = result + int(arg)
        print "result="+str(result)
        sys.exit(0)

    elif cmd_args[0].lower() == "mul":
        result = 1;
        for arg in cmd_args[1:]:
            result = result * int(arg)
        print "result="+str(result)
        sys.exit(0)
    else:
        print "error: unknown command"
        sys.exit(-1)
except ValueError:
    print "error: unexpected input"
    sys.exit(-1)
